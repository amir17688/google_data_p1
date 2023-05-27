#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import ImproperlyConfigured
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.test import LiveServerTestCase as DjangoLiveServerTestCase
from django.test import TransactionTestCase as DjangoTransactionTestCase
from django.test import TestCase as DjangoTestCase
from django.utils.translation import activate

from djangobmf.conf import settings
from djangobmf.demo import FIXTURES
from djangobmf.sites import site

from collections import OrderedDict

import json

# from unittest import expectedFailure


class BaseTestCase(object):

    def setUp(self):  # noqa
        activate('en')
        site.activate(test=True)
        super(BaseTestCase, self).setUp()

    def create_user(self, username, is_staff=False, is_superuser=False,
                    is_active=True, permissions=None, create_employee=True):
        """
        This method is used to create users in test cases
        """
        user = get_user_model()
        username_field = user.USERNAME_FIELD

        fields = {
            'email': username + '@test.django-bmf.org',
            'is_staff': is_staff,
            'is_active': is_active,
            'is_superuser': is_superuser,
        }

        # Check for special case where email is used as username
        # if username_field != 'email':
        fields[username_field] = username

        user_obj = user(**fields)
        user_obj.set_password(getattr(user_obj, username_field))
        user_obj.save()

        # create employee object for user
        try:
            apps.get_model(settings.CONTRIB_EMPLOYEE).objects.create(user=user_obj)
        except LookupError:
            pass

        if not is_superuser and permissions:
            for permission in permissions:
                user_obj.user_permissions.add(Permission.objects.get(codename=permission))

        return user_obj

    def client_login(self, username):
        # Check for special case where email is used as username
        # if get_user_model().USERNAME_FIELD == 'email':
        #     username += '@test.django-bmf.org'

        # update client
        self.client.login(username=username, password=username)


class DemoDataMixin(object):
    """
    Adds the demo data from the fixtures to the testcase
    """
    fixtures = FIXTURES


class SuperuserMixin(object):
    """
    Adds a superuser to the clients and authenticates itself with this user
    """

    def setUp(self):  # noqa
        super(SuperuserMixin, self).setUp()
        self.user = self.create_user("superuser", is_superuser=True)
        self.client_login("superuser")


class ModuleTestFactory(SuperuserMixin, BaseTestCase):
    """
    Test generic module views within app-config ``app``

    Currently detail, get and list views are tested.

    The test includes only the template rendering of those classes. No
    data is accessed or changed.
    """

    # the modules app config
    app = None

    def setUp(self):  # noqa
        super(BaseTestCase, self).setUp()
        self.user = self.create_user("superuser", is_superuser=True)
        self.client_login("superuser")
        self.appconf = [app for app in apps.get_app_configs() if isinstance(app, self.app)][0]
        self.models = [m for m in self.appconf.get_models() if m in site.models.values()]

    def test_module_create(self):
        for model in self.models:

            ns = model._bmfmeta.namespace_api

            for key, slug, view in site.modules[model].list_creates():
                url = reverse('%s:create' % ns, kwargs={
                    'key': key,
                })
                response = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
                self.assertEqual(response.status_code, 200)

    def test_module_report(self):
        for model in self.models:

            ns = model._bmfmeta.namespace_api

            for obj in model.objects.all():
                for key, slug, view in site.modules[model].list_reports():
                    url = reverse('%s:report' % ns, kwargs={
                        'pk': obj.pk,
                        'key': key,
                    })
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, 200)

    def test_module_update(self):
        for model in self.models:
            ns = model._bmfmeta.namespace_api

            for obj in model.objects.all():
                url = reverse('%s:update' % ns, kwargs={
                    'pk': obj.pk,
                })
                response = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
                self.assertTrue(response.status_code in [200, 403])

    def test_module_delete(self):
        for model in self.models:
            ns = model._bmfmeta.namespace_api

            for obj in model.objects.all():
                url = reverse('%s:delete' % ns, kwargs={
                    'pk': obj.pk,
                })
                response = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
                self.assertTrue(response.status_code in [200, 403])

    def test_module_api_data(self):
        for model in self.models:

            url = reverse('%s:api' % settings.APP_LABEL, kwargs={
                'app': model._meta.app_label,
                'model': model._meta.model_name,
            })
            response = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEqual(response.status_code, 200)

    def test_module_api_detail(self):
        for model in self.models:

            for obj in model.objects.all():
                url = reverse('%s:api-detail' % settings.APP_LABEL, kwargs={
                    'app': obj._meta.app_label,
                    'model': obj._meta.model_name,
                    'pk': obj.pk,
                })
                response = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
                self.assertTrue(response.status_code in [200])

    def test_module_api_related(self):
        self.appconf = [app for app in apps.get_app_configs() if isinstance(app, self.app)][0]

        for relation in self.appconf.bmf_config.bmf_relations:
            if relation._model not in self.models:
                continue

            for obj in relation._model.objects.all():
                url = reverse('%s:api-related' % settings.APP_LABEL, kwargs={
                    'app': obj._meta.app_label,
                    'model': obj._meta.model_name,
                    'pk': obj.pk,
                    'field': relation.slug,
                })
                response = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
                self.assertTrue(response.status_code in [200])

    def get_views(self):
        for model in self.models:
            for dashboard in site.dashboards:
                for category in dashboard:
                    for view in category:
                        if view.model == model:
                            yield (model, view, dashboard.key, category.key, view.key)

    def test_module_api_view(self):
        for v in self.get_views():
            url = reverse('%s:api-view' % settings.APP_LABEL, kwargs={
                'db': v[2],
                'cat': v[3],
                'view': v[4],
            })
            response = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEqual(response.status_code, 200)

    def test_module_dashboard_views(self):
        for v in self.get_views():
            url = reverse('%s:dashboard' % settings.APP_LABEL, kwargs={
                'dashboard': v[2],
                'category': v[3],
                'view': v[4],
            })
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)


class WorkflowTestFactory(SuperuserMixin, BaseTestCase):
    """
    """
    workflow = None

    def setUp(self):  # noqa
        super(BaseTestCase, self).setUp()
        self.user = self.create_user("superuser", is_superuser=True)
        self.client_login("superuser")
        self.prepare_workflow_test()

    def prepare_workflow_test(self):
        workflow = self.workflow()

        states = list(workflow._states.keys())
        states.remove(workflow._initial_state_key)
        heap = [
            (workflow._initial_state_key + '->' + key + '->' + transition.target)
            for key, transition in workflow._from_here()
        ]

        heap.reverse()
        self.objects = {workflow._initial_state_key: None}
        self.transitions = OrderedDict()

        while len(heap) > 0:
            current = heap.pop()
            obj, transition, target = current.split('->')
            self.transitions[current] = {
                'object': None,
                'object_key': obj,
                'state': obj.rsplit(':', 1)[-1],
                'user': None,
                'transition': transition,
            }

            if target in states:
                workflow._set_state(target)
                self.objects['%s:%s' % (obj, target)] = None
                for key, transition in workflow._from_here():
                    heap.insert(0, '%s:%s->%s->%s' % (
                        obj,
                        target,
                        key,
                        transition.target,
                    ))
                states.remove(target)

    def get_object(self, key):
        """
        return a new object copied from the one saved in self.objects
        """

        old = self.objects.get(key, None)

        if not old:
            raise ImproperlyConfigured(
                'No object given for key "%s"' % key
            )

        if not old.pk:
            old.save()

#       # use collector to copy related objects
#       # from django.contrib.admin.utils import NestedObjects
#       # collector = NestedObjects(using='default')
#       # collector.collect([obj])
#       # print(collector.nested())

        old.pk = None
        old.save()

        new = old._default_manager.get(pk=old.pk)

        return new

    def auto_workflow_test(self):
        for key, trans in self.transitions.items():

            obj = trans['object'] or self.get_object(trans['object_key'])

            if obj._bmfmeta.workflow.key != trans['state']:
                raise ImproperlyConfigured(
                    'Object "%s" is in the wrong state for transitions["%s"]' % (
                        obj,
                        key,
                    )
                )

            user = trans['user'] or self.user

            try:
                obj._bmfmeta.workflow.transition(trans['transition'], user, silent=True)
            except ValidationError as e:
                raise ImproperlyConfigured(
                    'Object "%s" raised a Validation error for transitions["%s"]: %s' % (
                        obj,
                        key,
                        e,
                    )
                )

            if trans['object_key']:
                new_key = '%s:%s' % (
                    trans['object_key'],
                    obj._bmfmeta.workflow.key
                )

                if not self.objects.get(new_key, None):
                    self.objects[new_key] = obj


class ModuleMixin(SuperuserMixin):
    model = None

    def get_latest_object(self):
        return self.model.objects.order_by('pk').last()

    def autotest_get(
            self, namespace=None, status_code=200, data=None, parameter=None,
            urlconf=None, args=None, kwargs=None, current_app=None, url=None, api=True):
        """
        tests the POST request of a view, returns the response
        """
        if api:
            ns = self.model._bmfmeta.namespace_api
        else:
            ns = self.model._bmfmeta.namespace_detail
        if not url:
            url = reverse(ns + ':' + namespace, urlconf, args, kwargs, current_app)
        if parameter:
            url += '?' + parameter
        r = self.client.get(url, data)
        self.assertEqual(r.status_code, status_code)
        return r

    def autotest_post(
            self, namespace=None, status_code=200, data=None, parameter=None,
            urlconf=None, args=None, kwargs=None, current_app=None, url=None, api=True):
        """
        tests the GET request of a view, returns the response
        """
        if api:
            ns = self.model._bmfmeta.namespace_api
        else:
            ns = self.model._bmfmeta.namespace_detail
        if not url:
            url = reverse(ns + ':' + namespace, urlconf, args, kwargs, current_app)
        if parameter:
            url += '?' + parameter
        r = self.client.post(url, data)
        self.assertEqual(r.status_code, status_code)
        return r

    def autotest_ajax_get(
            self, namespace=None, status_code=200, data=None, parameter=None,
            urlconf=None, args=None, kwargs=None, current_app=None, url=None, api=True):
        """
        tests the GET request of an ajax-view, returns the serialized data
        """
        if api:
            ns = self.model._bmfmeta.namespace_api
        else:
            ns = self.model._bmfmeta.namespace_detail
        if not url:
            url = reverse(ns + ':' + namespace, urlconf, args, kwargs, current_app)
        if parameter:
            url += '?' + parameter
        r = self.client.get(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, status_code)
        if status_code == 200:
            return json.loads(r.content.decode())
        return r

    def autotest_ajax_post(
            self, namespace=None, status_code=200, data=None, parameter=None,
            urlconf=None, args=None, kwargs=None, current_app=None, url=None, api=True):
        """
        tests the POST request of an ajax-view, returns the serialized data
        """
        if api:
            ns = self.model._bmfmeta.namespace_api
        else:
            ns = self.model._bmfmeta.namespace_detail
        if not url:
            url = reverse(ns + ':' + namespace, urlconf, args, kwargs, current_app)
        if parameter:
            url += '?' + parameter
        r = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, status_code)
        if status_code == 200:
            return json.loads(r.content.decode())
        return r


class TestCase(BaseTestCase, DjangoTestCase):
    pass


class TransactionTestCase(BaseTestCase, DjangoTransactionTestCase):
    pass


class LiveServerTestCase(BaseTestCase, DjangoLiveServerTestCase):
    pass
