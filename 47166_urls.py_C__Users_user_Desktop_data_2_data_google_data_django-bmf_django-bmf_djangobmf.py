#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

"""
This is a normal urlconf. it is imported from djangobmf.sites.site.get_url, where
the module views get appended by an '^module/' expression
"""

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.utils.timezone import now
from django.views.decorators.cache import cache_page
from django.views.decorators.cache import never_cache
# from django.views.decorators.vary import vary_on_cookie
from django.views.decorators.http import last_modified

from djangobmf import get_version
from djangobmf.core.views.activity import View as APIActivityListView
from djangobmf.core.views.detail import View as APIDetailView
from djangobmf.core.views.document import View as APIDocumentsView
from djangobmf.core.views.related import View as APIRelatedView
from djangobmf.sites import site
from djangobmf.views import Index
from djangobmf.views.api import APIIndex
from djangobmf.views.api import APIViewDetail
from djangobmf.views.api import APIModuleListView
# from djangobmf.views.api import APIModuleDetailView
from djangobmf.views.api import NotificationCountAPI
from djangobmf.views.api import NotificationListAPI
from djangobmf.views.api import NotificationViewAPI
from djangobmf.views.configuration import ConfigurationView
from djangobmf.views.configuration import ConfigurationEdit
from djangobmf.views.dashboard import DashboardIndex
from djangobmf.views.dashboard import Redirect
# from djangobmf.views.dashboard import DashboardCategory
# from djangobmf.views.dashboard import DashboardView
from djangobmf.views.wizard import WizardView


VERSION = get_version()


if settings.DEBUG:
    CACHE_TIME = 1
else:
    CACHE_TIME = 86400  # 24h


@cache_page(CACHE_TIME, key_prefix=VERSION)
@last_modified(lambda req, **kw: now())
def i18n_javascript(request):
    """
    Displays the i18n JavaScript that the Django admin requires.
    """
    if settings.USE_I18N:  # pragma: no cover
        from django.views.i18n import javascript_catalog
    else:  # pragma: no cover
        from django.views.i18n import null_javascript_catalog as javascript_catalog
    return javascript_catalog(request, packages=['djangobmf'])


urlpatterns = patterns(
    '',
    # VIEWS COVERED BY UI
    url(
        r'^$',
        Index.as_view(), name="dashboard"
    ),
    url(
        r'^dashboard/(?P<dashboard>[\w-]+)/(?P<category>[\w-]+)/(?P<view>[\w-]+)/$',
        Index.as_view(),
        name="dashboard",
    ),
    url(
        r'^dashboard/(?P<dashboard>[\w-]+)/(?P<category>[\w-]+)/(?P<view>[\w-]+)/(?P<pk>[0-9]+)/$',
        Index.as_view(),
        name="dashboard",
    ),

    url(
        r'^dashboard/(?P<dashboard>[\w-]+)/$',
        DashboardIndex.as_view(),
        name="dashboard",
    ),
    url(
        r'^notification/$',
        Index.as_view(),
        name="notification",
    ),
    url(
        r'^notification/(?P<app>[\w]+)/(?P<model>[\w]+)/$',
        Index.as_view(),
        name="notification",
    ),
    url(
        r'^notification/(?P<app>[\w]+)/(?P<model>[\w]+)/(?P<pk>[0-9]+)/$',
        Index.as_view(),
        name="notification",
    ),
    url(
        r'^detail/(?P<app>[\w]+)/(?P<model>[\w]+)/(?P<pk>[0-9]+)/$',
        Index.as_view(),
    ),

    url(r'^accounts/', include('djangobmf.account.urls')),

    url(r'^router/', include(site.router.urls, namespace="router")),

    url(
        r'^api/$',
        never_cache(
            APIIndex.as_view()
        ),
        name="api",
    ),
    url(
        r'^api/data/(?P<app>[\w-]+)/(?P<model>[\w-]+)/$',
        never_cache(
            APIModuleListView.as_view()
        ),
        name="api",
    ),
    url(
        r'^api/detail/(?P<app>[\w-]+)/(?P<model>[\w-]+)/(?P<pk>[0-9]+)/$',
        never_cache(
            APIDetailView.as_view()
        ),
        name="api-detail",
    ),
    url(
        r'^api/related/(?P<app>[\w]+)/(?P<model>[\w]+)/(?P<field>[\w_]+)/(?P<pk>[0-9]+)/$',
        never_cache(
            APIRelatedView.as_view()
        ),
        name="api-related",
    ),
    url(
        r'^api/activity/(?P<app>[\w]+)/(?P<model>[\w]+)/(?P<pk>[0-9]+)/$',
        never_cache(
            APIActivityListView.as_view()
        ),
        name="api-activity",
    ),
    url(
        r'^api/notification/(?P<app>[\w]+)/(?P<model>[\w]+)/view/$',
        never_cache(
            NotificationViewAPI.as_view()
        ),
        name="api-notification",
        kwargs={'action': 'view'},
    ),
    url(
        r'^api/notification/(?P<app>[\w]+)/(?P<model>[\w]+)/view/(?P<pk>[0-9]+)/$',
        never_cache(
            NotificationViewAPI.as_view()
        ),
        name="api-notification",
        kwargs={'action': 'view'},
    ),
    url(
        r'^api/notification/count/$',
        never_cache(
            NotificationCountAPI.as_view()
        ),
        name="api-notification",
        kwargs={'action': 'count'},
    ),
    url(
        r'^api/notification/(?P<app>[\w]+)/(?P<model>[\w]+)/list/$',
        never_cache(
            NotificationListAPI.as_view()
        ),
        name="api-notification",
        kwargs={'action': 'list'},
    ),
    url(
        r'^api/view/(?P<db>[\w-]+)/(?P<cat>[\w-]+)/(?P<view>[\w-]+)/$',
        cache_page(CACHE_TIME, key_prefix=VERSION)(
            last_modified(lambda req, **kw: now())(
                APIViewDetail.as_view()
            )
        ),
        name="api-view",
    ),
    url(
        r'^api/documents/(?P<app>[\w]+)/(?P<model>[\w]+)/(?P<pk>[0-9]+)/$',
        APIDocumentsView.as_view({'get': 'list', 'post': 'create'}),
        name="api-documents",
    ),
    url(
        r'^api/documents/$',
        APIDocumentsView.as_view({'get': 'list', 'post': 'create'}),
        name="api-documents",
    ),
    url(
        r'^api/documents/(?P<pk>[0-9]+)/$',
        APIDocumentsView.as_view({
            'get': 'retrieve',
            'patch': 'partial_update',
            'put': 'update',
            'delete': 'destroy',
        }),
        name="api-documents",
    ),
    url(
        r'^api/documents/(?P<pk>[0-9]+)/download/$',
        APIDocumentsView.as_view({
            'get': 'download',
        }),
        name="api-document-download",
    ),

    # --- Configuration
    url(
        r'^config/$', ConfigurationView.as_view(), name="configuration",
    ),
    url(
        r'^config/(?P<app_label>[\w]+)/(?P<name>[\w]+)/$',
        ConfigurationEdit.as_view(), name="configuration",
    ),

    url(
        r'^detail/$',
        Redirect.as_view(), name="detail",
    ),
    url(
        r'^detail/(?P<model_name>[\w]+)/$',
        Redirect.as_view(), name="detail",
    ),
    url(
        r'^detail/(?P<model_name>[\w]+)/(?P<app_label>[\w]+)/$',
        Redirect.as_view(), name="detail",
    ),
    #   r'^detail/' via sites

    # --- Dashboard
    #   url(
    #       r'^dashboard/(?P<dashboard>[\w-]+)/(?P<category>[\w-]+)/$',
    #       DashboardCategory.as_view(),
    #       name="dashboard",
    #   ),
    #   r'^dashboard/(?P<dashboard>[\w-]+)/' via sites


    url(r'^i18n/', i18n_javascript, name="jsi18n"),
    #  url(r'^messages/', include('djangobmf.message.urls')),
    url(r'^wizard/$', WizardView.as_view(), name="wizard"),
)
