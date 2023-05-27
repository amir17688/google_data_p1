import time
from dateutil import parser
from datetime import datetime, timedelta, date
from causal.main.handlers import OAuthServiceHandler
from causal.main.models import OAuth, RequestToken, AccessToken, UserService, ServiceItem
from causal.main.utils.services import get_model_instance, get_url, generate_days_dict
from causal.main.exceptions import LoggedServiceError
from django.utils.datastructures import SortedDict

class ServiceHandler(OAuthServiceHandler):
    """Handle all service requests for github"""
    
    def setup(self):
        """Disable ssl cert checking"""
        self.disable_ssl = True
    
    display_name = 'Github'

    def _get_feed(self):
        """Fetch the json feed for a user from github.com"""

        username, name = self._get_details()
        feed = self.get_data('https://github.com/%s.json' % (username))
        
        return feed
    
    def get_items(self, since):
        """Fetch updates.
        """

        feed = self._get_feed()
        
        if feed:
            return self._convert_feed(feed, since)

    def get_stats_items(self, since):
        """Fetch stats updates.
        """

        feed = self._get_feed()
        
        if feed:
            return self._convert_stats_feed(feed, since)

    def _get_repos(self, since):
        """Fetch the repo list for a user."""
        
        repos_url = "https://api.github.com/user/repos?access_token=%s" % (self.service.auth.access_token.oauth_token)
        repos = get_url(repos_url)
        
        updated_repos = []
        for repo in repos:
            pushed = datetime.strptime(repo['pushed_at'], '%Y-%m-%dT%H:%M:%SZ')
            if pushed.date() > since:
                updated_repos.append(repo)
                
        return updated_repos
    
    def _convert_feed(self, feed, since):
        """Take the user's atom feed.
        """
        
        items = []

        for entry in feed:
            if entry.has_key('public') and entry['public']:
                
                if entry.has_key('created_at'):
                    created = self._convert_date(entry['created_at'])

                if created.date() >= since:
                    item = ServiceItem()
                    self._set_title_body(entry, item)
                    item.created = created
                    if entry['type'] == 'GistEvent':
                        item.link_back = entry['payload']['url']
                    else:
                        if entry.has_key('url'):
                            item.link_back = entry['url']
                    item.service = self.service
                    items.append(item)

        return items

    def _convert_date(self, date_time):
        """Convert the date given in a commit api call."""
        
        if date_time:
            if date_time.find('T') < 0:
                date, time, offset = date_time.rsplit(' ')
                direction = offset[0]
                offset = offset[1:]
                time_format = '%Y/%m/%d %H:%M:%S'
            else:
                date, time_and_offset = date_time.rsplit('T')
                time = time_and_offset[:8]
                offset = time_and_offset[9:]
                direction = time_and_offset[8]
                time_format = '%Y-%m-%d %H:%M:%S'
            
            if direction == '-':
                direction = '+'
            elif direction == '+':
                direction = '-'
                
            time_offset = timedelta(hours=int(direction + offset[:2]))

            return datetime.strptime(date + ' ' + time, time_format) + time_offset

    def _convert_stats_feed(self, feed, since):
        """Take the user's atom feed.
        """

        items = []
        commits = []
        commit_times = {}
        repos = {}
        avatar = ""
        
        list_of_commits = {}
        
        username, name = self._get_details()
        
        if not username or not feed:
            return 

        if feed and feed[0]['actor_attributes'].has_key('gravatar_id'):
            avatar = 'http://www.gravatar.com/avatar/%s' % (feed[0]['actor_attributes']['gravatar_id'],)

        days_committed = generate_days_dict()
                
        for entry in feed:
            if entry['public']:
                dated, time, offset = entry['created_at'].rsplit(' ')
                if entry.has_key('created_at'):
                    created = self._convert_date(entry['created_at'])

                if created.date() >= since:
                    if entry.has_key('repository') \
                       and entry['repository'].has_key('name') \
                       and entry['repository'].has_key('owner'):
                        url = "https://api.github.com/repos/%s/%s?" % (
                            entry['repository']['owner'],
                            entry['repository']['name'])
                        repo = self.get_data(url)
                        if repo:                
                            repos[entry['repository']['owner'] + entry['repository']['name']] = repo
                        
                    # extract commits from push event
                    if entry['type'] == 'PushEvent':
                        
                        # fetch and get the stats on commits
                        for commit in entry['payload']['shas']:
                            
                            # test it we have seen the commit before
                            if not list_of_commits.has_key(commit[0]):
                                list_of_commits[commit[0]] = True
                                item = ServiceItem()
                                if name == commit[-1]:
                                    commit_detail = None
                                    if entry.has_key('repository'):
                                        url = "https://api.github.com/repos/%s/%s/git/commits/%s?" % (
                                            entry['repository']['owner'],
                                            entry['repository']['name'], 
                                            commit[0])
                                        
                                        commit_detail = self.get_data(url)
                                        item.body = '"%s"' % (commit_detail['message'])
                                    
                                        item.title = "Commit for %s" % (entry['repository']['name'])
                                    else:
                                        if entry['type'] == 'PushEvent':
                                            item.title = "Push for %s" % (entry['url'].split('/')[4])
                                            item.body = entry['payload']['shas'][0][2]
                                    
                                    if commit_detail and commit_detail.has_key('author') and commit_detail['author'].has_key('date'):
                                        item.created = self._convert_date(commit_detail['author']['date'])
                                    else:
                                        item.created = self._convert_date(entry['created_at'])
                                    # tag entry as private as the repo is marked private
                                    if repo and repo.has_key('private'):
                                        item.private = repo['private']
                                    
                                    if commit_detail and commit_detail.has_key('url'):
                                        # https://github.com/bassdread/causal/commit/7aef64a152ec28846111612620b6042b21615423
                                        #item.link_back = "https://github.com/%s/%s/commit/%s" %(entry['repository']['owner'], entry['repository']['name'], commit[0])
                                        item.link_back = commit_detail['url']
                                    else:
                                        item.link_back = entry['url']
        
                                    item.service = self.service
                                    commits.append(item)
                                    
                                    if days_committed.has_key(item.created_local.date()):
                                        days_committed[item.created_local.date()] = days_committed[item.created_local.date()] + 1
                                
                                    hour = item.created_local.strftime('%H')
                                    if commit_times.has_key(hour):
                                        commit_times[hour] += 1
                                    else:
                                        commit_times[hour] = 1
                                        
                                    del(item)
                    else:
                        item = ServiceItem()
                        self._set_title_body(entry, item)
                        item.created = created
                        if entry.has_key('url'):
                            item.link_back = entry['url']
                        item.service = self.service
                        items.append(item)

        commit_times = SortedDict(sorted(
            commit_times.items(),
            reverse=True,
            key=lambda x: x[1]
        ))
        
        days_committed = SortedDict(sorted(days_committed.items(), reverse=False, key=lambda x: x[0]))
        max_commits_on_a_day = SortedDict(sorted(days_committed.items(), reverse=True, key=lambda x: x[1]))
        max_commits_on_a_day = max_commits_on_a_day[max_commits_on_a_day.keyOrder[0]] + 1
        commits.sort(key=lambda commit: commit.created_local, reverse=True)
        
        return { 'events' : items,
                 'commits' : commits, 
                 'avatar' : avatar, 
                 'commit_times' : commit_times,
                 'most_common_commit_time' : self._most_common_commit_time(commit_times), 
                 'days_committed' : days_committed, 
                 'max_commits_on_a_day' : max_commits_on_a_day, 
                 'repos' : repos}
    
    def _most_common_commit_time(self, commits):
        """Take a list of commit times and return the most common time
        of commits."""
        
        if not commits:
            return False
        
        hour = commits.keys()[0]
        
        if hour == '23':
            return '%s:00 and 00:00' % (hour)
        else:
            return '%s:00 and %s:00' % (hour, int(hour) + 1)
    
    def _set_title_body(self, entry, item):
        """Set the title and body based on the event type."""

        item.body = ''
        
        try:
            if entry['type'] == 'CreateEvent':
                if entry['payload'].has_key('object_name'):
                    item.title = "Created branch %s from %s" % (entry['payload']['object_name'], entry['payload']['name'])
                else:
                    if entry.has_key('repository'):
                        item.title = "Created branch %s from %s" % (entry['payload']['master_branch'], entry['repository']['name'])  
                    else:
                        item.title = "Created branch %s from %s" % (entry['payload']['master_branch'], entry['payload']['ref'])
            elif entry['type'] == 'GistEvent':
                item.title = "Created gist %s" % (entry['payload']['desc'])
            elif entry['type'] == 'IssuesEvent':
                url = 'https://github.com/%s/%s/issues/%s' % (
                    entry['repository']['owner'], 
                    entry['repository']['name'],
                    str(entry['payload']['number']))
                item.title = 'Issue <a href="%s">#%s</a> was %s.' % (url, str(entry['payload']['number']), entry['payload']['action'])
            elif entry['type'] == 'ForkEvent':
                item.title = "Repo %s forked." % (entry['repository']['name'])
            elif entry['type'] == 'PushEvent':
                if entry.has_key('repository'):
                    item.title = "Pushed to repo %s with comment \"%s\"." % (entry['repository']['name'], entry['payload']['shas'][0][2])
                else:
                    item.title = entry['url'].split('/')[4]
            elif entry['type'] == 'CreateEvent':
                item.title = "Branch %s for %s." % (entry['payload']['object_name'], entry['payload']['name'])
            elif entry['type'] == 'WatchEvent':
                item.title = "Started watching %s." % (entry['repository']['name'])
            elif entry['type'] == 'FollowEvent':
                item.title = "Started following %s." % (entry['payload']['target']['login'])
            elif entry['type'] == 'GistEvent':
                item.title = "Snippet: %s" % (entry['payload']['snippet'])
            elif entry['type'] == 'DeleteEvent':
                item.title = "Deleted: %s called %s" % (entry['payload']['ref_type'], entry['payload']['ref'])
            elif entry['type'] == 'GollumEvent':
                pass
            elif entry['type'] == 'IssueCommentEvent':
                comments = get_url('https://api.github.com/repos/%s/%s/issues/comments/%s' % (
                    entry['repository']['owner'], 
                    entry['repository']['name'],
                    entry['payload']['comment_id']
                ))
                item.title = '<b>Commented</b> "%s" on issue <a href="%s">%s</a>' % (comments['body'], entry['url'], entry['url'].split('#')[0].rsplit('/', 1)[1])
            elif entry['type'] == 'PullRequestEvent':
                item.title = "Created pull for %s" % (entry['repository']['name'])
            else:
                item.title = "Unknown Event!"
                
        except:
            item.title = "Unknown Event!"
            
    def _get_details(self):
        """Get a user's profile data"""
        
        user_json = self.get_data('https://api.github.com/user?')
        
        if user_json and user_json.has_key('login') and user_json.has_key('name'):
            return user_json['login'], user_json['name']