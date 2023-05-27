#!/usr/bin/python
# ex:set fileencoding=utf-8:
# flake8: noqa

from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from djangobmf.urls import i18n_javascript
from djangobmf.utils.testcases import TestCase


class UrlTests(TestCase):
    def test_i18n_javascript(self):
        r = self.client.get(reverse('djangobmf:jsi18n'))
        self.assertEqual(r.status_code, 200)
