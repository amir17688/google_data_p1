#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django.conf.urls import patterns
from django.conf.urls import url
from django.utils import six
from django.utils.text import slugify

from djangobmf.permissions import ModulePermission
# from djangobmf.views import ModuleCloneView
from djangobmf.views import ModuleCreateView
from djangobmf.views import ModuleDeleteView
from djangobmf.views import ModuleDetail
from djangobmf.views import ModuleFormAPI
# from djangobmf.views import ModuleReportView
from djangobmf.views import ModuleUpdateView
from djangobmf.views import ModuleWorkflowView

import logging
logger = logging.getLogger(__name__)


class ModuleMetaclass(type):
    def __new__(cls, name, bases, attrs):
        super_new = super(ModuleMetaclass, cls).__new__
        parents = [
            b for b in bases if isinstance(b, ModuleMetaclass) and
            not (b.__name__ == 'NewBase' and b.__mro__ == (b, object))
        ]
        if not parents:
            return super_new(cls, name, bases, attrs)

        # Create the class.
        new_cls = super_new(cls, name, bases, attrs)

        # validation
        if not getattr(new_cls, 'model', None):
            raise ImproperlyConfigured('No model defined in %s.' % new_cls)

        if not hasattr(new_cls.model, '_bmfmeta'):
            raise ImproperlyConfigured(
                'The module %s needs to be an BMF-Model in order to be'
                'registered with django BMF.' % new_cls.model.__name__
            )

        return new_cls


class Module(six.with_metaclass(ModuleMetaclass, object)):
    """
    Object internally used to register modules
    """
    detail = ModuleDetail
    create = ModuleCreateView
    delete = ModuleDeleteView
    update = ModuleUpdateView
    permissions = ModulePermission

    clone = None
    primary = True
    report = None
    default = False

    detail_urlpatterns = None
    api_urlpatterns = None

    def __init__(self):
        self.dashboards = []
        self.manager = {}
        self.detail_view = self.detail.as_view(model=self.model)

        self.create_view = self.create
        self.delete_view = self.delete
        self.update_view = self.update

    def list_reports(self):
        if hasattr(self, 'listed_reports'):
            return self.listed_reports
        self.listed_reports = []

#       if isinstance(self.report, dict):
#           for label, view in six.iteritems(self.report):
#               key = slugify(label)
#               if isinstance(view, (list, tuple)) and len(view) == 2:
#                   # overwrite the label, and correct the view
#                   label = slugify(view[0])
#                   view = view[1]

#               if issubclass(view, ModuleReportView):
#                   self.listed_reports.append((key, label, view))

#       elif isinstance(self.report, bool):
#           self.listed_reports.append(('default', 'default', ModuleReportView))

#       elif self.report and issubclass(self.report, ModuleReportView):
#           self.listed_reports.append(('default', 'default', self.report))

        # update model with all report views
        self.model._bmfmeta.report_views = self.listed_reports

        return self.listed_reports

    def list_creates(self):
        if hasattr(self, 'listed_creates'):
            return self.listed_creates
        self.listed_creates = []

        if isinstance(self.create, dict):
            for label, view in six.iteritems(self.create):
                key = slugify(label)

                if isinstance(view, (list, tuple)) and len(view) == 2:
                    # overwrite the label, and use the correct the view function
                    label = view[0]
                    view = view[1]
                self.listed_creates.append((key, label, view))

        elif issubclass(self.create, ModuleCreateView):
            self.listed_creates.append(('default', 'default', self.create))

        # update model with all create views
        self.model._bmfmeta.create_views = self.listed_creates

        return self.listed_creates

    def get_detail_urls(self):
        # add custom url patterns
        if self.detail_urlpatterns:
            return self.detail_urlpatterns
        return patterns('')

    def get_api_urls(self):
        reports = self.list_reports()
        creates = self.list_creates()

        urlpatterns = patterns(
            '',
            url(
                r'^update/(?P<pk>[0-9]+)/$',
                self.update.as_view(
                    module=self,
                    model=self.model
                ),
                name='update',
            ),
            url(
                r'^update/(?P<pk>[0-9]+)/form/$',
                ModuleFormAPI.as_view(
                    module=self,
                    model=self.model,
                    form_view=self.update,
                ),
                name='update-form',
            ),
            url(
                r'^delete/(?P<pk>[0-9]+)/$',
                self.delete.as_view(
                    module=self,
                    model=self.model
                ),
                name='delete',
            ),
        )

        if self.model._bmfmeta.can_clone:
            urlpatterns += patterns(
                '',
                url(
                    r'^clone/(?P<pk>[0-9]+)/$',
                    self.clone.as_view(
                        module=self,
                        model=self.model
                    ),
                    name='clone',
                ),
                url(
                    r'^clone/(?P<pk>[0-9]+)/form/$',
                    ModuleFormAPI.as_view(
                        module=self,
                        model=self.model,
                        form_view=self.clone,
                    ),
                    name='clone-form',
                ),
            )

        for key, label, view in creates:
            urlpatterns += patterns(
                '',
                url(
                    r'^create/(?P<key>%s)/$' % key,
                    view.as_view(
                        module=self,
                        model=self.model
                    ),
                    name='create',
                ),
                url(
                    r'^create/(?P<key>%s)/form/$' % key,
                    ModuleFormAPI.as_view(
                        module=self,
                        model=self.model,
                        form_view=view,
                    ),
                    name='create-form',
                ),
            )

        for key, label, view in reports:
            urlpatterns += patterns(
                '',
                url(
                    r'^report/(?P<pk>[0-9]+)/(?P<key>%s)/$' % key,
                    view.as_view(
                        module=self,
                        model=self.model
                    ),
                    name='report',
                ),
            )

        # workflow interactions
        if self.model._bmfmeta.has_workflow:
            urlpatterns += patterns(
                '',
                url(
                    r'^workflow/(?P<pk>[0-9]+)/(?P<transition>\w+)/$',
                    ModuleWorkflowView.as_view(
                        module=self,
                        model=self.model
                    ),
                    name='workflow',
                ),
            )

        # add custom url patterns
        if self.api_urlpatterns:
            urlpatterns += self.api_urlpatterns

        return urlpatterns
