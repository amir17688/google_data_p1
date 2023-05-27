#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from djangobmf.conf import settings
from djangobmf.contrib.accounting.models import ACCOUNTING_LIABILITY
from djangobmf.models import BMFModel

from decimal import Decimal

from .serializers import TaxSerializer


@python_2_unicode_compatible
class AbstractTax(BMFModel):
    name = models.CharField(max_length=255, null=False, blank=False, )
    # invoice_name_long = models.CharField( max_length=255, null=False, blank=False, )
    # invoice_name_short = models.CharField( max_length=255, null=False, blank=False, )
    account = models.ForeignKey(
        settings.CONTRIB_ACCOUNT, null=False, blank=False, related_name="tax_liability",
        limit_choices_to={'type': ACCOUNTING_LIABILITY, 'read_only': False},
        on_delete=models.PROTECT,
    )
    rate = models.DecimalField(max_digits=8, decimal_places=5)
    is_active = models.BooleanField(_("Is active"), null=False, blank=False, default=True)

    def get_rate(self):
        return self.rate / Decimal(100)

    class Meta:
        verbose_name = _('Tax')
        verbose_name_plural = _('Taxes')
        ordering = ['name']
        abstract = True
        swappable = "BMF_CONTRIB_TAX"

    class BMFMeta:
        observed_fields = ['name', 'invoice_name', 'rate']
        serializer = TaxSerializer

    def __str__(self):
        return self.name


class Tax(AbstractTax):
    pass
