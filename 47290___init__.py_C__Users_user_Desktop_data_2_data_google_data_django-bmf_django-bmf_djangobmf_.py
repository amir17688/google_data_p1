#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.db import models as django_models
from django.forms.widgets import TextInput
from django.utils.translation import ugettext_lazy as _
from django.utils.six import with_metaclass

from djangobmf.conf import settings
from djangobmf.currency import BaseCurrency

# from .configobj import ConfigField
from djangobmf.fields.country import CountryField
from djangobmf.fields.file import FileField
from djangobmf.fields.file import ObjectFileField
from djangobmf.fields.file import StaticFileField
from djangobmf.fields.workflow import WorkflowField

import logging
logger = logging.getLogger(__name__)


__all__ = [
    'OLDWorkflowField',
    'ConfigField',
    'CountryField',
    'WorkflowField',
    'CurrencyField',
    'MoneyField',
    'FileField',
    'ObjectFileField',
    'StaticFileField',
]


# Currency and Money
# -----------------------------------------------------------------------------
# see: http://blog.elsdoerfer.name/2008/01/08/fuzzydates-or-one-django-model-field-multiple-database-columns/


def get_default_currency():
    return settings.DEFAULT_CURRENCY


class MoneyProxy(object):
    def __init__(self, field):
        self.field = field

    def __get__(self, obj, type=None):
        if obj is None:
            raise AttributeError('Can only be accessed via an instance.')
        return obj.__dict__[self.field.name]

    def __set__(self, obj, value):

        # get currency model
        currency = getattr(obj, self.field.get_currency_field_name())

        if self.field.has_precision:
            precision = getattr(obj, self.field.get_precision_field_name())
        else:
            precision = 0

        if currency is not None and not isinstance(value, BaseCurrency):
            value = currency.__class__(value, precision=precision)

        obj.__dict__[self.field.name] = value


class CurrencyField(with_metaclass(django_models.SubfieldBase, django_models.CharField)):
    description = _("Currency Field")

    def __init__(self, *args, **kwargs):
        defaults = {
            'max_length': 4,
            'editable': False,
        }
        defaults.update(kwargs)
        defaults.update({
            'null': True,
            'blank': False,
            'default': get_default_currency,
        })
        super(CurrencyField, self).__init__(*args, **defaults)

    def to_python(self, value):
        if isinstance(value, BaseCurrency):
            return value

        # The string case.
        from djangobmf.sites import site
        return site.currencies['%s' % (value or settings.DEFAULT_CURRENCY)]()
        # except ImportError:
        #    logger.debug('Sites not available, returning no currency class')
        #    return None

    def get_prep_value(self, obj):
        if hasattr(obj, 'iso'):
            return obj.iso
        return None

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)

    def deconstruct(self):
        name, path, args, kwargs = super(CurrencyField, self).deconstruct()
        del kwargs["null"]
        del kwargs["default"]
        return name, path, args, kwargs


class MoneyField(django_models.DecimalField):
    description = _("Money Field")

    def __init__(self, *args, **kwargs):
        defaults = {
            'default': None,
            'blank': True,
        }
        defaults.update(kwargs)
        defaults.update({
            'null': True,
            'max_digits': 27,
            'decimal_places': 9,
        })
        super(MoneyField, self).__init__(*args, **defaults)

    def to_python(self, value):
        if isinstance(value, BaseCurrency):
            return value.value
        return super(MoneyField, self).to_python(value)

    def get_currency_field_name(self):
        return '%s_currency' % self.name

    def get_precision_field_name(self):
        return '%s_precision' % self.name

    def deconstruct(self):
        name, path, args, kwargs = super(MoneyField, self).deconstruct()
        del kwargs["null"]
        del kwargs["max_digits"]
        del kwargs["decimal_places"]
        return name, path, args, kwargs

    def contribute_to_class(self, cls, name):
        super(MoneyField, self).contribute_to_class(cls, name)
        if not cls._meta.abstract:
            self.has_precision = hasattr(self, self.get_precision_field_name())
            setattr(cls, self.name, MoneyProxy(self))

    def formfield(self, **kwargs):
        kwargs.update({
            'widget': TextInput,
        })
        value = super(MoneyField, self).formfield(**kwargs)
        return value

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)

    def get_prep_value(self, value):
        if isinstance(value, BaseCurrency):
            value = value.value
        super(MoneyField, self).get_prep_value(value)

    def get_db_prep_save(self, value, *args, **kwargs):
        if isinstance(value, BaseCurrency):
            value = value.value
        return super(MoneyField, self).get_db_prep_save(value, *args, **kwargs)


class OLDWorkflowField(with_metaclass(django_models.SubfieldBase, django_models.CharField)):
    """
    OLD DONT USE ITS GOING TO BE REMOVED, WITH DJANGOBMF 0.0.3 or 0.0.4
    """
    description = "Workflow field"

    def __init__(self, **kwargs):
        # TODO ADD REMOVAL WARNING
        defaults = {
            'max_length': 32,  # max length
            'db_index': True,
        }
        defaults.update(kwargs)
        defaults.update({
            'null': True,
            'blank': True,
            'editable': False,
        })
        super(OLDWorkflowField, self).__init__(**defaults)
