from django.conf.urls.defaults import *

base_path = r'^flickr/'
shortcut = 'flickr-urls'

urlpatterns = patterns('',
    url(r'^$', 'causal.flickr.views.verify_auth', name='causal-flickr-callback'),
    url(r'^auth$', 'causal.flickr.views.auth', name='causal-flickr-auth'),
    url(r'^stats/(?P<service_id>\d+)$', 'causal.flickr.views.stats', name='causal-flickr-stats'),

)
