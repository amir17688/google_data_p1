# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('djangobmf_product', '0003_changed_verbose_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='producttax',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Created', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='producttax',
            name='created_by',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True, verbose_name='Created by'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='producttax',
            name='modified',
            field=models.DateTimeField(auto_now=True, verbose_name='Modified', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='producttax',
            name='modified_by',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True, verbose_name='Modified by'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='product',
            name='taxes',
            field=models.ManyToManyField(related_name='product_taxes', editable=False, to=settings.BMF_CONTRIB_TAX, through='djangobmf_product.ProductTax', blank=True),
            preserve_default=True,
        ),
    ]
