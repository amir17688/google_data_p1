#!/usr/bin/python
# ex:set fileencoding=utf-8:
# flake8: noqa

from __future__ import unicode_literals

from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from djangobmf.core.category import Category

from collections import OrderedDict


class ClassTests(TestCase):
    pass

#   def setUp(self):  # noqa

#       self.view1 = View(model='empty', name="Test1", slug="test1")
#       self.view2 = View(model='empty', name="Test2", slug="test2")

#       super(ClassTests, self).setUp()

#   def test_init_empty(self):
#       class TestCategory(Category):
#           name = "test"
#           slug = "test"
#       td = TestCategory()

#       self.assertEqual(td.data, OrderedDict([
#       ]))

#   def test_init_data1(self):
#       class TestCategory(Category):
#           name = "test"
#           slug = "test"
#       td = TestCategory(self.view1)

#       self.assertEqual(td.data, OrderedDict([
#           ('test1', self.view1),
#       ]))

#   def test_init_data2(self):
#       class TestCategory(Category):
#           name = "test"
#           slug = "test"
#       td = TestCategory(self.view1, self.view2)

#       self.assertEqual(td.data, OrderedDict([
#           ('test1', self.view1),
#           ('test2', self.view2),
#       ]))

#   def test_add_view(self):
#       class TestCategory(Category):
#           name = "test"
#           slug = "test"
#       td = TestCategory()

#       td.add_view(self.view1)
#       self.assertEqual(td.data, OrderedDict([
#           ('test1', self.view1),
#       ]))

#       td.add_view(self.view1)
#       self.assertEqual(td.data, OrderedDict([
#           ('test1', self.view1),
#       ]))

#       td.add_view(self.view2)
#       self.assertEqual(td.data, OrderedDict([
#           ('test1', self.view1),
#           ('test2', self.view2),
#       ]))

#       td.add_view(self.view1)
#       self.assertEqual(td.data, OrderedDict([
#           ('test1', self.view1),
#           ('test2', self.view2),
#       ]))

#       td.add_view(self.view2)
#       self.assertEqual(td.data, OrderedDict([
#           ('test1', self.view1),
#           ('test2', self.view2),
#       ]))

#   def test_key(self):
#       class TestCategory(Category):
#           name = "Test"
#           slug = "test"
#       td = TestCategory()
#       self.assertEqual(td.key, "test")

#   def test_merge(self):
#       class TestCategory1(Category):
#           name = "Test1"
#           slug = "test1"
#       class TestCategory2(Category):
#           name = "Test1"
#           slug = "test1"

#       td1 = TestCategory1()
#       td2 = TestCategory2()
#       td1.merge(td2)
#       self.assertEqual(td1.data, OrderedDict([
#       ]))

#       td1 = TestCategory1()
#       td2 = TestCategory2(self.view1)
#       td1.merge(td2)
#       self.assertEqual(td1.data, OrderedDict([
#           ('test1', self.view1),
#       ]))

#       td1 = TestCategory1(self.view1)
#       td2 = TestCategory2(self.view2)
#       td1.merge(td2)
#       self.assertEqual(td1.data, OrderedDict([
#           ('test1', self.view1),
#           ('test2', self.view2),
#       ]))

#       td1 = TestCategory1(self.view2)
#       td2 = TestCategory2(self.view2)
#       td1.merge(td2)
#       self.assertEqual(td1.data, OrderedDict([
#           ('test2', self.view2),
#       ]))

#       td1 = TestCategory1(self.view2, self.view1)
#       td2 = TestCategory2(self.view2)
#       td1.merge(td2)
#       self.assertEqual(td1.data, OrderedDict([
#           ('test2', self.view2),
#           ('test1', self.view1),
#       ]))

#   def test_bool(self):
#       class TestCategory(Category):
#           name = "test"
#           slug = "test"
#       td = TestCategory()
#       self.assertFalse(td)
#       td.add_view(self.view1)
#       self.assertTrue(td)

#   def test_len(self):
#       class TestCategory(Category):
#           name = "test"
#           slug = "test"

#       td = TestCategory()
#       self.assertEqual(len(td), 0)

#       td = TestCategory(self.view1, self.view2)
#       self.assertEqual(len(td), 2)

#   def test_eq(self):
#       class TestCategory1(Category):
#           name = "test1"
#           slug = "test1"
#       class TestCategory2(Category):
#           name = "test2"
#           slug = "test2"
#       class TestCategory3(Category):
#           name = "test1"
#           slug = "test1"

#       td1 = TestCategory1()
#       td2 = TestCategory2()
#       td3 = TestCategory3()

#       self.assertEqual(td1, td3)
#       self.assertNotEqual(td1, td2)
#       self.assertNotEqual(td1, self.view1)

#   def test_contains(self):
#       class TestCategory(Category):
#           name = "test"
#           slug = "test"
#       td = TestCategory(self.view1)
#       self.assertFalse('test2' in td)
#       self.assertFalse(self.view2 in td)
#       self.assertTrue('test1' in td)
#       self.assertTrue(self.view1 in td)

#   def test_getitem(self):
#       class TestCategory(Category):
#           name = "test"
#           slug = "test"
#       td = TestCategory(self.view1, self.view2)

#       self.assertEqual(td['test1'], self.view1)
#       self.assertEqual(td['test2'], self.view2)

#       with self.assertRaises(KeyError):
#           test = td['test3']

#   def test_iter(self):
#       class TestCategory(Category):
#           name = "test"
#           slug = "test"
#       td = TestCategory(self.view1)

#       for i in td:
#           self.assertEqual(i, self.view1)

#       td = TestCategory(self.view1, self.view2)
#       self.assertEqual([i for i in td], [self.view1, self.view2])
