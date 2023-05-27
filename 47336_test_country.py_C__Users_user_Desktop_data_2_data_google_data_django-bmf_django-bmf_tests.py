#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.test import TestCase
from django.test.utils import override_settings

from djangobmf.widgets.country import gettext
from djangobmf.widgets.country import CountryContainer
from djangobmf.widgets.country import CountrySelect


class GettextTests(TestCase):

    @override_settings(USE_I18N=False, LANGUAGE_CODE="de")
    def test_i18n_disabled(self):
        self.assertEqual(gettext('Italy'), 'Italy')

    @override_settings(USE_I18N=True, LANGUAGE_CODE="de")
    def test_i18n_enabled(self):
        self.assertEqual(gettext('Italy'), 'Italien')
        # the second call is needed to ensure branch coverage
        self.assertEqual(gettext('Spain'), 'Spanien')

    @override_settings(USE_I18N=True, LANGUAGE_CODE="de")
    def test_i18n_non_existing_country(self):
        self.assertEqual(gettext('UNDEFINED'), 'UNDEFINED')


@override_settings(USE_I18N=True, LANGUAGE_CODE="de")
class CountryContainerTests(TestCase):

    def setUp(self):  # noqa
        self.container = CountryContainer('CHE')

    def test_name(self):
        self.assertEqual(self.container.name, 'Schweiz')

    def test_official_name(self):
        self.assertEqual(self.container.official_name, 'Schweizerische Eidgenossenschaft')

    def test_int_name(self):
        self.assertEqual(self.container.int_name, 'Switzerland')

    def test_int_official_name(self):
        self.assertEqual(self.container.int_official_name, 'Swiss Confederation')

    def test_key(self):
        self.assertEqual(self.container.key, 'CHE')

    def test_alpha2(self):
        self.assertEqual(self.container.alpha2, 'CH')

    def test_alpha3(self):
        self.assertEqual(self.container.alpha3, 'CHE')

    def test_str(self):
        self.assertEqual('%s' % self.container, 'CHE')

    def test_len(self):
        self.assertEqual(len(self.container), 3)


@override_settings(USE_I18N=True, LANGUAGE_CODE="de")
class CountrySelectTests(TestCase):

    def test_empty_choices(self):
        select = CountrySelect()
        self.assertEqual(len(select.choices) > 0, True)

    def test_invalid_choice(self):
        with self.assertRaises(KeyError):
            CountrySelect(choices=('ESP', 'CHE', 'XY'))

    def test_defined_choices(self):
        select = CountrySelect(choices=('ESP', 'CHE', 'DEU'))
        self.assertEqual(select.choices, [
            ('DEU', 'Deutschland'),
            ('CHE', 'Schweiz'),
            ('ESP', 'Spanien')
        ])
