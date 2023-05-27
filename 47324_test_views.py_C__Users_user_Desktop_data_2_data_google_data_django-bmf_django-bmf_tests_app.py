#!/usr/bin/python
# ex:set fileencoding=utf-8:
# flake8: noqa

from __future__ import unicode_literals

from django.test import TestCase
from django.test.client import RequestFactory

# from djangobmf.views import ModuleListView
# from djangobmf.views import ModuleActivityMixin
# from djangobmf.views import ModuleFilesMixin
# from djangobmf.views import ModuleFormMixin
from djangobmf.views import ModuleReportView
from djangobmf.views import ModuleCloneView
from djangobmf.views import ModuleUpdateView
from djangobmf.views import ModuleCreateView
from djangobmf.views import ModuleDeleteView
from djangobmf.views import ModuleWorkflowView
from djangobmf.views import ModuleFormAPI
from djangobmf.views.defaults import bad_request
from djangobmf.views.defaults import permission_denied
from djangobmf.views.defaults import page_not_found
from djangobmf.views.defaults import server_error


from unittest import expectedFailure

from .models import TestView

class ViewsTests(TestCase):

#   def test_views_ModuleListView_get_template_names_default(self):
#       obj = ModuleListView()
#       obj.model = TestView
#       self.assertEqual(obj.get_template_names(), ['appapis/testview_bmfgeneric.html', 'djangobmf/module_generic.html'])

#   def test_views_ModuleListView_get_template_names_fixed(self):
#       obj = ModuleListView()
#       obj.model = TestView
#       obj.template_name = 'test.html'
#       self.assertEqual(obj.get_template_names(), ['test.html'])

    @expectedFailure
    def test_views_ModuleReportView(self):
        self.assertTrue(False)  # TODO NOT IMPLEMENTED

    @expectedFailure
    def test_views_ModuleCloneView(self):
        self.assertTrue(False)  # TODO NOT IMPLEMENTED

    @expectedFailure
    def test_views_ModuleUpdateView(self):
        self.assertTrue(False)  # TODO NOT IMPLEMENTED

    @expectedFailure
    def test_views_ModuleCreateView(self):
        self.assertTrue(False)  # TODO NOT IMPLEMENTED

    @expectedFailure
    def test_views_ModuleDeleteView(self):
        self.assertTrue(False)  # TODO NOT IMPLEMENTED

    @expectedFailure
    def test_views_ModuleWorkflowView(self):
        self.assertTrue(False)  # TODO NOT IMPLEMENTED

    @expectedFailure
    def test_views_ModuleFormAPI(self):
        self.assertTrue(False)  # TODO NOT IMPLEMENTED


class SimpleTest(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()

    def test_bad_request(self):
        request = self.factory.get('/400/')
        response = bad_request(request)
        self.assertEqual(response.status_code, 400)

    def test_permission_denied(self):
        request = self.factory.get('/403/')
        response = permission_denied(request)
        self.assertEqual(response.status_code, 403)

    def test_page_not_found(self):
        request = self.factory.get('/404/')
        response = page_not_found(request)
        self.assertEqual(response.status_code, 404)

    def test_server_error(self):
        request = self.factory.get('/500/')
        response = server_error(request)
        self.assertEqual(response.status_code, 500)
