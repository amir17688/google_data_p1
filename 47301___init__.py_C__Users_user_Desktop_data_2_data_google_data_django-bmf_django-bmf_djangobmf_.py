#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.db.models import signals
from django.dispatch import receiver

from djangobmf.conf import settings
from djangobmf.signals import activity_create
from djangobmf.signals import activity_update
from djangobmf.signals import activity_addfile
from djangobmf.signals import activity_workflow
from djangobmf.tasks import djangobmf_user_watch
from djangobmf.utils.serializers import DjangoBMFEncoder

import json

from .base import BMFModel
from .base import BMFModelBase

from .activity import ACTION_COMMENT
from .activity import ACTION_CREATED
from .activity import ACTION_UPDATED
from .activity import ACTION_WORKFLOW
from .activity import ACTION_FILE

from .activity import Activity as AbstractActivity
from .configuration import Configuration as AbstractConfiguration
from .document import Document as AbstractDocument
from .notification import Notification as AbstractNotification
from .numberrange import NumberRange as AbstractNumberRange
from .renderer import Renderer as AbstractRenderer
from .report import Report as AbstractReport


__all__ = (
    'BMFModel',
    'BMFModelBase',
    'ACTION_COMMENT',
    'ACTION_CREATED',
    'ACTION_UPDATED',
    'ACTION_WORKFLOW',
    'ACTION_FILE',
    'Activity',
    'Document',
    'Configuration',
    'Notification',
    'NumberCycle',
    'Renderer',
    'Report',
)


class Activity(AbstractActivity):
    class Meta(AbstractActivity.Meta):
        abstract = False
        app_label = settings.APP_LABEL


class Configuration(AbstractConfiguration):
    class Meta(AbstractConfiguration.Meta):
        abstract = False
        app_label = settings.APP_LABEL


# class Dashboard(AbstractDashboard):
#   class Meta(AbstractDashboard.Meta):
#       abstract = False
#       app_label = settings.APP_LABEL


class Document(AbstractDocument):
    class Meta(AbstractDocument.Meta):
        abstract = False
        app_label = settings.APP_LABEL


class Notification(AbstractNotification):
    class Meta(AbstractNotification.Meta):
        abstract = False
        app_label = settings.APP_LABEL


class NumberRange(AbstractNumberRange):
    class Meta(AbstractNumberRange.Meta):
        abstract = False
        app_label = settings.APP_LABEL


class Renderer(AbstractRenderer):
    class Meta(AbstractRenderer.Meta):
        abstract = False
        app_label = settings.APP_LABEL


class Report(AbstractReport):
    class Meta(AbstractReport.Meta):
        abstract = False
        app_label = settings.APP_LABEL


@receiver(activity_create)
def object_created(sender, instance, **kwargs):
    if instance._bmfmeta.has_logging:
        history = Activity(
            user=instance.created_by,
            parent_ct=ContentType.objects.get_for_model(sender),
            parent_id=instance.pk,
            action=ACTION_CREATED,
        )
        history.save()


@receiver(activity_update)
def object_changed(sender, instance, **kwargs):

    if instance._bmfmeta.has_logging and len(instance._bmfmeta.observed_fields) > 0:
        changes = []
        for key in instance._bmfmeta.observed_fields:
            try:
                if instance._bmfmeta.changelog[key] != getattr(instance, key):
                    changes.append((key, instance._bmfmeta.changelog[key], getattr(instance, key)))
            except KeyError:
                pass

        if len(changes) > 0:
            history = Activity(
                user=instance.modified_by,
                parent_ct=ContentType.objects.get_for_model(sender),
                parent_id=instance.pk,
                action=ACTION_UPDATED,
                text=json.dumps(changes, cls=DjangoBMFEncoder),
            )
            history.save()


@receiver(activity_workflow)
def new_state(sender, instance, **kwargs):
    if instance._bmfmeta.has_logging:
        history = Activity(
            user=instance.modified_by,
            parent_ct=ContentType.objects.get_for_model(sender),
            parent_id=instance.pk,
            action=ACTION_WORKFLOW,
            text=json.dumps({
                'old': instance._bmfmeta.workflow.initial,
                'new': instance._bmfmeta.workflow.key,
            }, cls=DjangoBMFEncoder),
        )
        history.save()


@receiver(activity_addfile)
def new_file(sender, instance, file, **kwargs):
    if instance._bmfmeta.has_logging:
        history = Activity(
            user=instance.modified_by,
            parent_ct=ContentType.objects.get_for_model(sender),
            parent_id=instance.pk,
            action=ACTION_FILE,
            text=json.dumps({
                'pk': file.pk,
                'size': file.size,
                'name': '%s' % file,
            }, cls=DjangoBMFEncoder),
        )
        history.save()


def activity_post_save(sender, instance, *args, **kwargs):
    djangobmf_user_watch(instance.pk)
signals.post_save.connect(activity_post_save, sender=Activity)
