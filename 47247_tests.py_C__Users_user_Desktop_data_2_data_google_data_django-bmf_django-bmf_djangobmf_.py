#!/usr/bin/python
# ex:set fileencoding=utf-8:
# flake8: noqa

from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType

from .apps import TaskConfig
from .models import Goal
from .models import Task
from .workflows import TaskWorkflow
from .workflows import GoalWorkflow

from djangobmf.utils.testcases import DemoDataMixin
from djangobmf.utils.testcases import TestCase
from djangobmf.utils.testcases import ModuleMixin
from djangobmf.utils.testcases import ModuleTestFactory
from djangobmf.utils.testcases import WorkflowTestFactory


class TaskFactory(ModuleTestFactory, DemoDataMixin, TestCase):
    app = TaskConfig


class GoalWorkflowFactory(WorkflowTestFactory, DemoDataMixin, TestCase):
    workflow = GoalWorkflow

    def test_goal_workflow_superuser(self):
        self.objects['open'] = Goal(summary="Test")
        self.auto_workflow_test()


class TaskWorkflowFactory(WorkflowTestFactory, DemoDataMixin, TestCase):
    workflow = TaskWorkflow

    def test_task_workflow_superuser(self):
        self.objects['new'] = Task(summary="Test")
        self.auto_workflow_test()


class TaskModuleTests(ModuleMixin, DemoDataMixin, TestCase):

    def test_goal_views(self):
        self.model = Goal
        data = self.autotest_ajax_post('create', kwargs={'key': 'default'}, data={'summary':'test'})

        obj = self.get_latest_object()
        a = '%s'%obj # check if object name has any errors

#       self.autotest_ajax_post('delete', kwargs={'pk': obj.pk}, data=None)

    def test_task_views(self):
        self.model = Task
        data = self.autotest_ajax_post('create', kwargs={'key': 'default'}, data={'summary':'test'})

        obj = self.get_latest_object()
        a = '%s'%obj # check if object name has any errors

#       self.autotest_ajax_post('delete', kwargs={'pk': obj.pk}, data=None)

    def test_goal_clone1(self):
        self.model = Goal

        obj = Goal(summary="test")
        obj.save()
        obj.task_set.create(summary="test1")
        obj.task_set.create(summary="test2")
        obj.task_set.create(summary="test3")
        data = self.autotest_ajax_post(
            'clone',
            kwargs={'pk': obj.pk},
            data={'summary':'test'},
        )

    def test_goal_clone2(self):
        self.model = Goal

        obj = Goal(summary="test")
        obj.save()
        obj.task_set.create(summary="test1")
        obj.task_set.create(summary="test2")
        obj.task_set.create(summary="test3")
        data = self.autotest_ajax_post(
            'clone',
            kwargs={'pk': obj.pk},
            data={'summary':'test', 'copy_tasks': True},
        )

    def test_goal_clone3(self):
        self.model = Goal

        obj = Goal(summary="test")
        obj.save()
        obj.task_set.create(summary="test1")
        obj.task_set.create(summary="test2")
        obj.task_set.create(summary="test3")
        data = self.autotest_ajax_post(
            'clone',
            kwargs={'pk': obj.pk},
            data={'summary':'test', 'copy_tasks': True, 'clear_employee': True},
        )

    def test_task_workflows(self):
        """
        """
        goal1 = Goal(summary="Goal1", project_id=1)
        goal1.clean()
        goal1.save()

        goal2 = Goal(summary="Goal2", project_id=1, referee_id=2)
        goal2.clean()
        goal2.save()

        goal2.bmfget_customer()
        goal2.bmfget_project()

        goal3 = Goal(summary="Goal3")
        goal3.clean()
        goal3.save()

        goal3.bmfget_customer()

        task1 = Task(summary="Task1", goal=goal1)
        task1.clean()
        task1.save()

        task2 = Task(summary="Task2", goal=goal2)
        task2.clean()
        task2.save()

        task3 = Task(summary="Task3", project_id=1)
        task3.clean()
        task3.save()

        Project = task3.project._default_manager

        task3.get_goal_queryset(Goal.objects.all())

        task4 = Task(summary="Task4")
        task4.clean()
        task4.save()

        task5 = Task(summary="Task5", due_date='2014-01-01')
        task5.clean()
        task5.save()

        task5.get_project_queryset(Project.all())
        task5.get_goal_queryset(Goal.objects.all())

        task6 = Task(summary="Task6", due_date='2014-01-01', goal=goal1)
        task6.clean()
        task6.save()

        task6.get_project_queryset(Project.all())

        task7 = Task(summary="Task7", goal=goal1, employee_id=1)
        task7.clean()
        task7.save()

        task8 = Task(summary="Task8", due_date='3014-01-01', goal=goal1)
        task8.clean()
        task8.save()

#       namespace = Task._bmfmeta.namespace_api

#       r = self.client.get(reverse(namespace+':workflow', None, None, {'pk': task1.pk, 'transition': 'start'}))
#       self.assertEqual(r.status_code, 302)

#       r = self.client.get(reverse(namespace+':workflow', None, None, {'pk': task2.pk, 'transition': 'finish'}))
#       self.assertEqual(r.status_code, 302)

#       # r = self.client.get(reverse(namespace+':workflow', None, None, {'pk': task2.pk, 'transition': 'finish'}))
#       # self.assertEqual(r.status_code, 200)

#       # r = self.client.get(reverse(namespace+':workflow', None, None, {'pk': task2.pk, 'transition': 'unreview'}))
#       # self.assertEqual(r.status_code, 302)

#       # r = self.client.get(reverse(namespace+':workflow', None, None, {'pk': task2.pk, 'transition': 'finish'}))
#       # self.assertEqual(r.status_code, 302)

#       # r = self.client.get(reverse(namespace+':workflow', None, None, {'pk': task4.pk, 'transition': 'hold'}))
#       # self.assertEqual(r.status_code, 302)

#       r = self.client.get(reverse(namespace+':workflow', None, None, {'pk': task3.pk, 'transition': 'start'}))
#       self.assertEqual(r.status_code, 302)

#       r = self.client.get(reverse(namespace+':workflow', None, None, {'pk': task3.pk, 'transition': 'stop'}))
#       self.assertEqual(r.status_code, 302)

#       r = self.client.get(reverse(namespace+':workflow', None, None, {'pk': task3.pk, 'transition': 'finish'}))
#       self.assertEqual(r.status_code, 302)

#       r = self.client.get(reverse(namespace+':workflow', None, None, {'pk': task6.pk, 'transition': 'hold'}))
#       self.assertEqual(r.status_code, 302)

#       r = self.client.get(reverse(namespace+':workflow', None, None, {'pk': task7.pk, 'transition': 'cancel'}))
#       self.assertEqual(r.status_code, 302)

#       r = self.client.get(reverse(namespace+':workflow', None, None, {'pk': task7.pk, 'transition': 'reopen'}))
#       self.assertEqual(r.status_code, 302)

#       r = self.client.get(reverse(namespace+':workflow', None, None, {'pk': task7.pk, 'transition': 'finish'}))
#       self.assertEqual(r.status_code, 302)

#       namespace = Goal._bmfmeta.namespace_detail
#       # r = self.client.get(reverse(namespace + ':index'))
#       #self.assertEqual(r.status_code, 200)

#       r = self.client.get(reverse(namespace+':detail', None, None, {'pk': goal1.pk}))
#       self.assertEqual(r.status_code, 200)
#    
#       r = self.client.get(reverse(namespace+':detail', None, None, {'pk': goal2.pk}))
#       self.assertEqual(r.status_code, 200)

#       namespace = Task._bmfmeta.namespace_api
#       #r = self.client.get(reverse(namespace + ':index'))
#       #self.assertEqual(r.status_code, 200)

##      r = self.client.get(reverse(namespace + ':create'))
##      self.assertEqual(r.status_code, 200)

#       namespace = Goal._bmfmeta.namespace_api

#       r = self.client.get(reverse(namespace+':workflow', None, None, {'pk': goal1.pk, 'transition': 'complete'}))
#       self.assertEqual(r.status_code, 200)
