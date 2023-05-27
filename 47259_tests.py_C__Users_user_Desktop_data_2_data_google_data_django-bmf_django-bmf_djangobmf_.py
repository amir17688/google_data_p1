#!/usr/bin/python
# ex:set fileencoding=utf-8:
# flake8: noqa

from __future__ import unicode_literals

from .apps import TeamConfig
from .models import Team

from djangobmf.utils.testcases import DemoDataMixin
from djangobmf.utils.testcases import TestCase
from djangobmf.utils.testcases import ModuleMixin
from djangobmf.utils.testcases import ModuleTestFactory


class TeamFactory(ModuleTestFactory, DemoDataMixin, TestCase):
    app = TeamConfig


class TeamModuleTests(ModuleMixin, TestCase):

    def test_urls_user(self):
        """
        """
        self.model = Team

#       data = self.autotest_ajax_get('create', kwargs={'key': 'default'})
#       data = self.autotest_ajax_post('create', kwargs={'key': 'default'}, data={
#           'name': 'test',
#       })
#       self.assertNotEqual(data["object_pk"], 0)

#       obj = self.get_latest_object()
#       a = '%s'%obj  # check if object name has any errors

#       self.autotest_get('detail', kwargs={'pk': obj.pk}, api=False)
#       data = self.autotest_ajax_get('update', kwargs={'pk': obj.pk})
#       self.autotest_get('delete', kwargs={'pk': obj.pk})
#       self.autotest_post('delete', status_code=302, kwargs={'pk': obj.pk})
