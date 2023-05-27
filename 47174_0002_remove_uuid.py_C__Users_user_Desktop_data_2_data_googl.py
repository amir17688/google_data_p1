# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import djangobmf.fields


class Migration(migrations.Migration):

    dependencies = [
        ('djangobmf_accounting', '0001_version_0_2_0'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='uuid',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='uuid',
        ),
        migrations.RemoveField(
            model_name='transactionitem',
            name='uuid',
        ),
        migrations.AlterField(
            model_name='account',
            name='balance',
            field=djangobmf.fields.MoneyField(editable=False, default=None, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='transactionitem',
            name='amount',
            field=djangobmf.fields.MoneyField(blank=True, default=None),
            preserve_default=True,
        ),
    ]
