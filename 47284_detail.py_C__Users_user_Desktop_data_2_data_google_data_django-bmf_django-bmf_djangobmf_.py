#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.apps import apps
from djangobmf.conf import settings

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.reverse import reverse

from djangobmf.core.permissions import DetailPermission
from djangobmf.core.views.mixins import BaseMixin
from djangobmf.models import Notification

from collections import OrderedDict


class View(BaseMixin, GenericAPIView):
    permission_classes = [DetailPermission]
    bmfconfig = apps.get_app_config(settings.APP_LABEL)

    def dispatch(self, *args, **kwargs):
        self.get_bmfmodel()
        return super(View, self).dispatch(*args, **kwargs)

    def get_serializer_class(self):
        if hasattr(self.model, '_bmfmeta'):
            return self.model._bmfmeta.serializer_class
        raise RuntimeError(
            'You need to use a model managed by djangobmf'
        )

    def get(self, request, *args, **kwargs):
        self.object = self.get_bmfobject(self.kwargs.get('pk', None))
        serialized = self.get_serializer_class()(self.object)
        meta = self.object._bmfmeta
        module = self.bmfconfig.bmf_modules[self.object.__class__]
        related_response = module.detail_view(request, object=self.object)

        try:
            notification = Notification.objects.get(
                user=self.request.user,
                watch_ct=self.get_bmfcontenttype(),
                watch_id=self.object.pk
            )
            if notification.unread:
                notification.unread = False
                notification.save()
        except Notification.DoesNotExist:
            pass

        return Response(OrderedDict([
            ('object', serialized.data),
            ('html', related_response.rendered_content.strip()),
            ('views', {
                'update': reverse(
                    'djangobmf:moduleapi_%s_%s:update' % (
                        self.object._meta.app_label,
                        self.object._meta.model_name,
                    ),
                    format=None,
                    request=self.request,
                    kwargs={'pk': self.object.pk},
                ),
                'delete': reverse(
                    'djangobmf:moduleapi_%s_%s:delete' % (
                        self.object._meta.app_label,
                        self.object._meta.model_name,
                    ),
                    format=None,
                    request=self.request,
                    kwargs={'pk': self.object.pk},
                ),
            }),
            ('workflow', meta.workflow.serialize(self.request) if meta.workflow else None),
        ]))
