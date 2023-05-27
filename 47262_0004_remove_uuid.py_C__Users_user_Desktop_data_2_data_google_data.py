# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djangobmf_team', '0003_teammember_to_bmfmodel'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='team',
            name='uuid',
        ),
        migrations.RemoveField(
            model_name='teammember',
            name='uuid',
        ),
    ]
