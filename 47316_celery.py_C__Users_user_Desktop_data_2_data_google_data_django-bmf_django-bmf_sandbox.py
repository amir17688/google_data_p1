#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals
from __future__ import absolute_import

import os

from celery import Celery

from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sandbox.settings_venv')

app = Celery('sandbox')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
