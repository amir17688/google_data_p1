"""Communicate with Facebook and fetch various updates.
We use FQL to fetch results from Facebook.
"""

from causal.main.handlers import OAuthServiceHandler
from causal.main.exceptions import LoggedServiceError
from causal.main.models import ServiceItem, AccessToken
from causal.main.utils.services import get_model_instance, get_url
from datetime import datetime, timedelta
from django.shortcuts import redirect
from django.utils import simplejson
from facegraph.fql import FQL
import httplib2
import time

# fetch all statuses for a user
STATUS_FQL = """SELECT uid,status_id,message,time FROM status WHERE uid = me() AND time > %s"""

# links posted
LINKED_FQL = """SELECT owner_comment,created_time,title,summary,url FROM link WHERE owner=me() AND created_time > %s"""

# users stream needs fixing
STREAM_FQL = """SELECT likes,message,created_time,comments,permalink,privacy,source_id FROM stream WHERE filter_key IN (SELECT filter_key FROM stream_filter WHERE uid = me() AND type="newsfeed") AND created_time > %s"""

# fetch username
USER_NAME_FETCH = """SELECT name, pic_small FROM user WHERE uid=%s"""

# fetch uid
USER_ID = """SELECT uid FROM user WHERE uid = me()"""

class ServiceHandler(OAuthServiceHandler):
    display_name = 'Facebook'

    def setup(self):
        """Disable ssl cert checking"""
        pass   
    
    def get_items(self, since):
        """Fetch main stats for history page."""

        status_stream = self.get_data('https://graph.facebook.com/me/statuses')
        link_stream = self.get_data('https://graph.facebook.com/me/links')
        like_stream = self.get_data('https://graph.facebook.com/me/likes')

        items = []
        
        if status_stream:
            items = self._convert_status_feed(status_stream, since)
        
        if link_stream:
            items += self._convert_link_feed(link_stream, since)
        
        if like_stream:
            items += self._convert_likes_feed(like_stream, since)
        
        return items

    def get_stats_items(self, since):
        """Return more detailed ServiceItems for the stats page."""

        items = {
            'links' : [],
            'statuses' : [],
            'likes' : [],
            'photos' : [],
            'albums' : [],
            'checkins' : [],
        }
        
        link_stream = self.get_data('https://graph.facebook.com/me/links')
        if link_stream:
            items['links'] = self._convert_link_feed(link_stream, since)

        status_stream = self.get_data('https://graph.facebook.com/me/statuses')
        if status_stream:
            items['statuses'] = self._convert_status_feed(status_stream, since)
        
        like_stream = self.get_data('https://graph.facebook.com/me/likes')
        if like_stream:
            items['likes'] += self._convert_likes_feed(like_stream, since)

        photo_stream = self.get_data('https://graph.facebook.com/me/photos')
        if photo_stream:
            items['photos'] += self._convert_photos_feed(photo_stream, since)
        
        album_stream = self.get_data('https://graph.facebook.com/me/albums')
        if album_stream:
            items['albums'] += self._convert_albums_feed(album_stream, since)

        checkin_stream = self.get_data('https://graph.facebook.com/me/checkins')
        if checkin_stream:
            items['checkins'] += self._convert_checkin_feed(checkin_stream, since)            
            
        return items

    def _convert_checkin_feed(self, checkins, since):
        """Sort out the checkin feed"""
        
        items = []

        for checkin in checkins['data']:
            if checkin.has_key('created_time'):
                created = self._convert_time_stamp(checkin['created_time'])

                if created.date() >= since:
                    item = ServiceItem()
                    item.created = created
                    item.link_back = 'http://www.facebook.com/%s' % (checkin['place']['id'])
                    
                    if checkin.has_key('place') and checkin['place'].has_key('name'):
                        item.title = checkin['place']['name']

                    item.service = self.service
                    items.append(item)

        return items

    def _convert_link_feed(self, links, since):
        """Convert link feed."""

        items = []

        for link in links['data']:
            if link.has_key('created_time'):
                created = self._convert_time_stamp(link['created_time'])

                if created.date() >= since:
                    item = ServiceItem()
                    item.created = created
                    item.link_back = link['link']
                    
                    if link.has_key('message'):
                        item.body = link['message']

                    item.url = link['link']
                    item.service = self.service
                    items.append(item)

        return items
    
    def _convert_photos_feed(self, photos, since):
        """Convert photo feed."""

        items = []

        for photo in photos['data']:
            if photo.has_key('created_time'):
                created = self._convert_time_stamp(photo['created_time'])

                if created.date() >= since:
                    item = ServiceItem()
                    item.created = created
                    item.link_back = photo['link']
                    item.title = photo['name']
                        
                    if photo.has_key('images'):
                        try:
                            item.body = photo['images'][3]
                        except:
                            pass

                    item.url = photo['link']
                    item.tags = []
                    
                    if photo.has_key('tags'):
                        for tag in photo['tags']['data']:
                            item.tags.append(tag['name'])
                        
                    item.comments = []
                    if photo.has_key('comments'):
                        for comment in photo['comments']['data']:
                            item.comments.append({'name' : comment['from']['name'],
                                                  'message' : comment['message'] })
                        
                    item.service = self.service
                    items.append(item)

        return items

    def _convert_time_stamp(self, date):
        """convert facebook's datetime '2011-08-05T12:02:09+0000' into python style,
         """
        try:
            offset = date[-5:]
            direction = offset[0]
    
            # work if we are adding time on or not
            if direction == '-':
                direction = '+'
            elif direction == '+':
                direction = '-'
                
            time_offset = timedelta(hours=int(direction + offset[1:5]))
            return datetime.strptime(date[:-5], '%Y-%m-%dT%H:%M:%S') + time_offset
        except:
            pass
    
    def _convert_status_feed(self, statuses, since):
        """Take the feed of status updates from facebook and convert it to
        ServiceItems."""

        items = []

        for status in statuses['data']:
            
            if status.has_key('message'):
                
                if not status.has_key('updated_time'):
                    pass
                else:
                    created = self._convert_time_stamp(status['updated_time'])
                    if created.date() >= since:
                        item = ServiceItem()
                        item.created = created
                        item.title = ''
                        item.body = status['message']
                        item.link_back = \
                            "http://www.facebook.com/%s/posts/%s?notif_t=feed_comment" % (status['from']['id'], status['id'])
                        item.service = self.service
                        items.append(item)

        return items
    
    def _convert_likes_feed(self, likes, since):
        """fetch using a cheeky url grab"""
        
        items = []
        
        # get info about the like:
        # https://graph.facebook.com/271847211041
        
        for like in likes['data']:
            
            if like.has_key('created_time'):
                created = self._convert_time_stamp(like['created_time'])
                
                if created.date() >= since:
                    
                    info_on_like = get_url('https://graph.facebook.com/%s' % (like['id']))
                    
                    item = ServiceItem()
                    item.created = created
                    
                    if like.has_key('name'):
                        item.title = like['name']
                        
                    if like.has_key('category'):    
                        item.body = like['category']
                        
                    item.link_back = info_on_like['link']
                    item.service = self.service
                    items.append(item)
            else:
                pass
        return items
    
    def _convert_albums_feed(self, albums, since):
        """Find new albums and display the pics"""
        
        items = []
        
        for album in albums['data']:
            
            if album.has_key('created_time'):
                created = self._convert_time_stamp(album['created_time'])
                
                if created.date() >= since:

                    
                    # fetch likes
                    #https://graph.facebook.com/album['id']/likes
                    #https://graph.facebook.com/photo['cover_photo']
                    
                    item = ServiceItem()
                    item.created = created
                    
                    if album.has_key('cover_photo'):
                        info_on_photo = self.get_data('https://graph.facebook.com/%s' % (album['cover_photo']))
                        if info_on_photo and info_on_photo.has_key('images'):
                            try:
                                item.body = info_on_photo['images'][3]
                            except:
                                pass
                            
                    album_likes = self.get_data('https://graph.facebook.com/%s/likes' % (album['id']))
                    
                    if album_likes:
                        item.likes = []
                        for like in album_likes['data']:
                            user = self.get_data('https://graph.facebook.com/%s' % (like['id']))
                            item.likes.append({like['name'] : user['link']})
                    
                    if album.has_key('name'):
                        item.title = album['name']
                        
                    item.link_back = album['link']
                    item.last_updated = self._convert_time_stamp(album['updated_time'])
                    item.service = self.service
                    item.number_of_photos = album['count']
                    items.append(item)
                    
        return items