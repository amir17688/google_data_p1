#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.conf import settings
from django.forms.widgets import Select
from django.utils.encoding import force_text
from django.utils.encoding import python_2_unicode_compatible
from django.utils.six import text_type
from django.utils.translation import get_language

import gettext as gettext_module
import pycountry
import unicodedata


# Translations are cached in a dictionary for every language.
_translations = {}


def gettext(value):
    global _translations

    if not settings.USE_I18N:
        return value

    language = get_language()
    if language not in _translations:
        _translations[language] = gettext_module.translation(
            domain='iso3166',
            localedir=pycountry.LOCALES_DIR,
            languages=[language],
            codeset='utf-8',
            fallback=True,
        )
    return _translations[language].gettext(value)


@python_2_unicode_compatible
class CountryContainer(object):
    """
    """

    def __init__(self, value):
        self.obj = pycountry.countries.get(alpha3=value)

    @property
    def name(self):
        return gettext(self.obj.name)

    @property
    def official_name(self):
        return gettext(self.obj.official_name)

    @property
    def int_name(self):
        return self.obj.name

    @property
    def int_official_name(self):
        return self.obj.official_name

    @property
    def key(self):
        return self.obj.alpha3

    @property
    def alpha2(self):
        return self.obj.alpha2

    @property
    def alpha3(self):
        return self.obj.alpha3

    def __str__(self):
        return text_type(self.obj.alpha3)

    def __len__(self):
        return 3


class CountrySelect(Select):
    def __init__(self, attrs=None, choices=()):
        super(Select, self).__init__(attrs)

        data = []
        if choices:
            for name in choices:
                data.append((name, gettext(pycountry.countries.get(alpha3=name).name)))
        else:
            for country in pycountry.countries:
                data.append((country.alpha3, gettext(country.name)))

        self.choices = list(sorted(
            data,
            key=lambda x: unicodedata.normalize('NFKD', force_text(x[1]))
        ))
