import httplib2
import oauth2 as oauth
from datetime import datetime, timedelta
from causal.main.handlers import OAuthServiceHandler
from causal.main.models import ServiceItem
from causal.main.utils.services import get_model_instance
from causal.main.exceptions import LoggedServiceError
from django.contrib import messages
from django.shortcuts import render_to_response, redirect
from datetime import datetime
from django.utils.datastructures import SortedDict

class ServiceHandler(OAuthServiceHandler):
    display_name = 'Foursquare'

    def get_items(self, since):
        """Fetch the history of checkins for the current user.
        """

        try:
            checkins = self.get_data('https://api.foursquare.com/v2/users/self/checkins')
        except Exception, e:
            return LoggedServiceError(original_exception=e)

        return self._convert_feed(checkins, since)

    def _get_mayorships(self):
        """Get everywhere the user is mayor"""
        
        items = []
        mayorships = self.get_data('https://api.foursquare.com/v2/users/self/mayorships')
        for checkin in mayorships['response']['mayorships']['items']:
            items.append(self._create_checkin(checkin))

        return items
    
    def get_stats_items(self, since):
        """Stubbed out for now"""

        checkins = self.get_items(since)

        categories = {}
        badge_images = {}
        mayorships = self._get_mayorships()
        
        # use this to track if we have a twitter enabled user
        twitter_id = True
        
        user_details = self.get_data("https://api.foursquare.com/v2/users/self")
        
        if user_details:
            avatar = user_details['response']['user']['photo']
            twitter_id = ''
            if user_details['response']['user']['contact'].has_key('twitter') \
               and user_details['response']['user']['contact']['twitter']:
                user_id = user_details['response']['user']['contact']['twitter']
            else:
                user_id = user_details['response']['user']['id']
                twitter_id = False
        try:
            badges = self.get_data("https://api.foursquare.com/v2/users/self/badges")
            badge_images = self._pick_badges(badges, user_id, twitter_id)
            
        except Exception, e:
            return LoggedServiceError(original_exception=e)
        
        for checkin in checkins:
                    
            if hasattr(checkin, 'categories'):
                if categories.has_key(checkin.categories[0]['name']):
                    categories[checkin.categories[0]['name']]['count'] += 1
                else:
                    if hasattr(checkin, 'icon'):
                        icon = checkin.icon
                    else:
                        icon = checkin.categories[0]['name']
                    categories[checkin.categories[0]['name']] = {
                    'icon' : icon,
                    'count' : 1
                    }
                    
        categories = SortedDict(sorted(categories.items(), reverse=True, key=lambda x: x[1]))
                    
        return checkins, categories, mayorships, badge_images
    
    def _pick_badges(self, badges, user_id, twitter=False):
        """Extract and build the links to their images over at foursquare."""

        badge_images = {}
        
        if badges.has_key('response') and badges['response'].has_key('badges'):
            for k,v in badges['response']['badges'].iteritems():
                
                if v.has_key('unlocks') and v['unlocks']:
                    if twitter:
                        badge_url = 'https://foursquare.com/%s/badge/%s' % (user_id, k)
                    else:
                        badge_url = 'https://foursquare.com/user/%s/badges' % (user_id)
                    badge_images[v['name']] = {
                        'image' : v['image']['prefix'] + str(v['image']['sizes'][0]) + v['image']['name'],
                        'url' : badge_url
                    }
                    
        return badge_images
        
    def _convert_feed(self, json, since):
        """Take the raw json from the feed and convert it to ServiceItems.
        """

        items = []

        if json and json.has_key('response') and json['response'].has_key('checkins'):
            for checkin in json['response']['checkins']['items']:
                created = datetime.fromtimestamp(checkin['createdAt'])
                if created.date() >= since:
                    items.append(self._create_checkin(checkin))    

        return items

    def _create_checkin(self, checkin):
        """Convert a raw checkin into a service item"""
        
        item = ServiceItem()
        created = None
        if checkin.has_key('createdAt'):
            created = datetime.fromtimestamp(checkin['createdAt'])
        item.location = {}
        item.link_back = 'http://foursquare.com/venue/%s' % (checkin['venue']['id'],)
        item.title = checkin['venue']['name']
        
        if checkin['venue'].has_key('location') and checkin['venue']['location'].has_key('city'):
            item.city = checkin['venue']['location']['city']

        if checkin.has_key('shout') and checkin['shout']:
            item.body = checkin['shout']
        else:
            if len(checkin['venue']['categories']) > 0 and checkin['venue']['location'].has_key('city'):
                item.body = "A %s in %s" % (checkin['venue']['categories'][0]['name'], checkin['venue']['location']['city'])
            elif checkin['venue'].has_key('city'):
                item.body = "In %s" % (checkin['venue']['location']['city'])
            else:
                item.body = "%s" % (checkin['venue']['name'])

        if checkin['venue']['location'].has_key('lat') and checkin['venue']['location']['lng']:
            item.location['lat'] = checkin['venue']['location']['lat']
            item.location['long'] = checkin['venue']['location']['lng']

        if created:
            item.created = created
        item.service = self.service
        
        if checkin.has_key('isMayor'):
            item.is_mayor = checkin['isMayor']
        else:
            pass

        if checkin['venue'].has_key('categories') and len(checkin['venue']['categories']) > 0:
            item.icon = checkin['venue']['categories'][0]['icon']
            item.categories = checkin['venue']['categories']
        
        return item