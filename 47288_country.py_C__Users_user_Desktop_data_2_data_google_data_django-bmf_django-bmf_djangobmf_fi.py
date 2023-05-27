#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from djangobmf.widgets import CountrySelect
from djangobmf.widgets.country import CountryContainer


class CountryField(models.CharField):
    """
    """
    description = _("Country Field")
    default_error_messages = {
        'invalid_country': _('%(name)s is not a valid 3-char country code'),
    }

    def __init__(self, *args, **kwargs):
        defaults = {
            'blank': False,
            'editable': True,
        }
        defaults.update(kwargs)
        defaults.update({
            'null': True,
            'max_length': 3,
        })
        super(CountryField, self).__init__(**defaults)

    def deconstruct(self):
        name, path, args, kwargs = super(CountryField, self).deconstruct()
        del kwargs["null"]
        del kwargs["max_length"]
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        defaults = {
            'widget': CountrySelect(),
        }
        defaults.update(kwargs)
        return super(CountryField, self).formfield(**defaults)

    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return None
        return self.string_to_country(value)

    def string_to_country(self, value):
        try:
            return CountryContainer(value)
        except KeyError:
            raise ValidationError(
                self.error_messages['invalid_country'],
                code='invalid_country',
                params={'name': value}
            )

    def to_python(self, value):
        if not value:
            return None

        if isinstance(value, CountryContainer):
            return value

        return self.string_to_country(value)

    def get_prep_value(self, value):
        if isinstance(value, CountryContainer):
            return value.key
        return value

    def value_to_string(self, obj):
        """
        serialization
        """
        return self.get_prep_value(obj)
