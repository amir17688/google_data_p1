#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.apps import apps
from django.forms import BooleanField
from django.forms import DateField
from django.forms import FloatField
from django.forms import ModelChoiceField
from django.forms import ModelForm
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from djangobmf.conf import settings
# from djangobmf.fields import CurrencyField
# from djangobmf.fields import MoneyField

from .models import Transaction
# from .models import TransactionItem


account_cls = apps.get_model(settings.CONTRIB_ACCOUNT)


class TransactionUpdateForm(ModelForm):
    class Meta:
        model = Transaction
        exclude = []


class TransactionCreateForm(ModelForm):

    date = DateField(label=_("Date"), initial=now)

    debit = ModelChoiceField(queryset=account_cls.objects.filter(read_only=False), empty_label=None)
    credit = ModelChoiceField(queryset=account_cls.objects.filter(read_only=False), empty_label=None)
    # amount_currency = CurrencyField()
    # amount = MoneyField()
    amount = FloatField(label=_("Amount"), min_value=0, localize=True)
    draft = BooleanField(label=_("Create draft"), initial=True, required=False)

    class Meta:
        model = Transaction
        exclude = []
