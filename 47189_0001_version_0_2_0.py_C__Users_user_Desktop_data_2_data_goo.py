# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    replaces = [
        ('djangobmf_customer','0001_initial'),
        ('djangobmf_customer','0002_optional_customer_project'),
        ('djangobmf_customer','0003_optional_customer_accounting'),
        ('djangobmf_customer','0004_version_0_2_0'),
    ]

    dependencies = [
        migrations.swappable_dependency(settings.BMF_CONTRIB_ACCOUNT),
        migrations.swappable_dependency(settings.BMF_CONTRIB_PROJECT),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('modified', models.DateTimeField(auto_now=True, null=True, verbose_name='Modified')),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created')),
                ('uuid', models.CharField(blank=True, null=True, db_index=True, max_length=100, editable=False, verbose_name='UUID')),
                ('name', models.CharField(max_length=255, verbose_name='Name', null=True)),
                ('number', models.CharField(blank=True, max_length=255, verbose_name='Number', null=True)),
                ('is_company', models.BooleanField(verbose_name='Is Company', default=False)),
                ('taxvat', models.CharField(blank=True, max_length=255, verbose_name='Taxvat', null=True)),
                ('use_company_addresses', models.BooleanField(verbose_name='Can use company adresses', default=True)),
                ('is_active', models.BooleanField(verbose_name='Is active', default=True)),
                ('is_customer', models.BooleanField(verbose_name='Is customer', default=True)),
                ('is_supplier', models.BooleanField(verbose_name='Is supplier', default=False)),
                ('customer_payment_term', models.PositiveSmallIntegerField(editable=False, default=1)),
                ('supplier_payment_term', models.PositiveSmallIntegerField(editable=False, default=1)),
                ('name2', models.CharField(blank=True, max_length=255, verbose_name='Name 2', null=True)),
                ('job_position', models.CharField(blank=True, max_length=255, verbose_name='Job position', null=True)),
                ('title', models.CharField(blank=True, max_length=255, verbose_name='Title', null=True)),
                ('phone_office', models.CharField(blank=True, max_length=255, verbose_name='Phone office', null=True)),
                ('phone_privat', models.CharField(blank=True, max_length=255, verbose_name='Phone privat', null=True)),
                ('phone_mobile', models.CharField(blank=True, max_length=255, verbose_name='Phone mobile', null=True)),
                ('email', models.EmailField(blank=True, max_length=75, verbose_name='Email', null=True)),
                ('fax', models.CharField(blank=True, max_length=255, verbose_name='Fax', null=True)),
                ('website', models.URLField(blank=True, verbose_name='Website', null=True)),
                ('notes', models.TextField(blank=True, verbose_name='Notes', null=True)),
                ('asset_account', models.ForeignKey(null=True, to=settings.BMF_CONTRIB_ACCOUNT, on_delete=django.db.models.deletion.PROTECT, related_name='customer_asset')),
                ('created_by', models.ForeignKey(blank=True, null=True, to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.SET_NULL, editable=False, related_name='+')),
                ('employee_at', models.ForeignKey(blank=True, null=True, to=settings.BMF_CONTRIB_CUSTOMER, on_delete=django.db.models.deletion.SET_NULL)),
                ('liability_account', models.ForeignKey(null=True, to=settings.BMF_CONTRIB_ACCOUNT, on_delete=django.db.models.deletion.PROTECT, related_name='customer_liability')),
                ('modified_by', models.ForeignKey(blank=True, null=True, to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.SET_NULL, editable=False, related_name='+')),
                ('project', models.ForeignKey(blank=True, null=True, to=settings.BMF_CONTRIB_PROJECT, help_text='Projects function as cost-centers. This setting defines a default project for this customer.', on_delete=django.db.models.deletion.PROTECT, related_name='+')),
                ('user', models.ForeignKey(blank=True, null=True, to=settings.AUTH_USER_MODEL, unique=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bmf_customer')),
            ],
            options={
                'abstract': False,
                'verbose_name_plural': 'Customers',
                'verbose_name': 'Customer',
                'ordering': ['name'],
                'swappable': 'BMF_CONTRIB_CUSTOMER',
            },
            bases=(models.Model,),
        ),
    ]
