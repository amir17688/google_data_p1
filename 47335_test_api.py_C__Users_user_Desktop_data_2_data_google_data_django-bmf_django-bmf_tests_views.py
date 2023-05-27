#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from djangobmf.utils.testcases import TestCase


class ViewApiTests(TestCase):

    def setUp(self):  # noqa
        super(ViewApiTests, self).setUp()
        self.user = self.create_user("user", is_superuser=True)

    def test_api_index(self):
        """
        """
        self.client_login("user")

        r = self.client.get(reverse('djangobmf:api'), {})
        self.assertEqual(r.status_code, 200)
