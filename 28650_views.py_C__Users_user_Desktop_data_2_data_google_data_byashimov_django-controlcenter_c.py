# -*- coding: utf-8 -*-

from importlib import import_module

from django.conf.urls import url
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ImproperlyConfigured
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView

from . import app_settings


class ControlCenter(object):
    def get_urls(self):
        self.dashboards = []
        for index, path in enumerate(app_settings.DASHBOARDS):
            pkg, name = path.rsplit('.', 1)
            klass = getattr(import_module(pkg), name)
            instance = klass(index)
            self.dashboards.append(instance)

        if not self.dashboards:
            raise ImproperlyConfigured('No dashboard found in '
                                       'settings.CONTROLCENTER_DASHBOARDS.')
        # Limits number to 10
        length = min([len(self.dashboards) - 1, 9])
        values = length and '[0-{}]'.format(length)
        urlpatterns = [
            url(r'^(?P<pk>{})/$'.format(values), dashboard_view,
                name='dashboard'),
        ]
        return urlpatterns

    @property
    def urls(self):
        # include(arg, namespace=None, app_name=None)
        return self.get_urls(), 'controlcenter', 'controlcenter'

controlcenter = ControlCenter()


class DashboardView(TemplateView):
    template_name = 'controlcenter/dashboard.html'

    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super(DashboardView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        pk = int(self.kwargs.get('pk'))
        self.dashboard = controlcenter.dashboards[pk]
        return super(DashboardView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = {
            'title': self.dashboard.title,
            'dashboard': self.dashboard,
            'dashboards': controlcenter.dashboards,
            'groups': self.dashboard.get_widgets(self.request),
            'sharp': app_settings.SHARP,
        }

        # Admin context
        kwargs.update(admin.site.each_context(self.request))
        kwargs.update(context)
        return super(DashboardView, self).get_context_data(**kwargs)

dashboard_view = DashboardView.as_view()
