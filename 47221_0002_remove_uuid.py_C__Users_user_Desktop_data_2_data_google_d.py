# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import djangobmf.fields


class Migration(migrations.Migration):

    dependencies = [
        ('djangobmf_product', '0001_version_0_2_0'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='uuid',
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=djangobmf.fields.MoneyField(default=None, verbose_name='Price', blank=True),
            preserve_default=True,
        ),
    ]
