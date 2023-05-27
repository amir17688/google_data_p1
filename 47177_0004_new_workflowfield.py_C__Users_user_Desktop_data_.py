# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import djangobmf.contrib.accounting.workflows
import djangobmf.fields


class Migration(migrations.Migration):

    dependencies = [
        ('djangobmf_accounting', '0003_changed_verbose_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='state',
            field=djangobmf.fields.WorkflowField(workflow=djangobmf.contrib.accounting.workflows.TransactionWorkflow, max_length=32, db_index=True),
            preserve_default=True,
        ),
    ]
