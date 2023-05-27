from django.conf.urls.defaults import *

base_path = r'^github/'
shortcut = 'github-urls'

urlpatterns = patterns('',
        url(r'^$', 'causal.github.views.verify_auth', name='causal-github-callback'),
        url(r'^auth$', 'causal.github.views.auth', name='causal-github-auth'),
        url(r'^stats/(?P<service_id>\d+)$', 'causal.github.views.stats', name='causal-github-stats'),
)
