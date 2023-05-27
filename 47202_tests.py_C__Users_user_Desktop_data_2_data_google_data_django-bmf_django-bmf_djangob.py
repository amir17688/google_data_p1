#!/usr/bin/python
# ex:set fileencoding=utf-8:
# flake8: noqa

from __future__ import unicode_literals

from django.test import LiveServerTestCase
from django.core.urlresolvers import reverse

from unittest import expectedFailure

from .apps import InvoiceConfig
from .models import Invoice

from djangobmf.utils.testcases import DemoDataMixin
from djangobmf.utils.testcases import TestCase
from djangobmf.utils.testcases import ModuleMixin
# from djangobmf.utils.testcases import WorkflowTestCase
from djangobmf.utils.testcases import ModuleTestFactory


class InvoiceFactory(ModuleTestFactory, DemoDataMixin, TestCase):
    app = InvoiceConfig


class InvoiceModuleTests(ModuleMixin, TestCase):

    def test_urls_user(self):
        """
        """
        self.model = Invoice

        data = self.autotest_ajax_get('create', kwargs={'key': 'default'})
       #data = self.autotest_ajax_post('create', data={
       #})
       #data = self.autotest_get('index')


#@expectedFailure
#class InvoiceWorkflowTests(WorkflowTestCase):
#    pass

   #def test_invoice_workflow(self):
   #    self.object = InvoiceFactory()
   #    workflow = self.workflow_build()
   #    workflow = self.workflow_autotest()
