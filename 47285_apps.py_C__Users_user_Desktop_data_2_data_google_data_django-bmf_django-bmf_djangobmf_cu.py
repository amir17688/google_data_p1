from __future__ import unicode_literals

from djangobmf.apps import CurrencyTemplate


class CurrencyConfig(CurrencyTemplate):
    name = 'djangobmf.currency.EUR'
    label = "EUR"
