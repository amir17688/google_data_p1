#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.conf import settings
from django.http import Http404

from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS


class AjaxPermission(BasePermission):
    """
    Only allow Ajax requests
    """
    def has_permission(self, request, view):
        return request.is_ajax() or settings.DEBUG

    def has_object_permission(self, request, view, obj):
        return request.is_ajax() or settings.DEBUG


class BaseModulePermission(BasePermission):
    """
    Permission object to check the module's permissions
    """
    _action = None
    _actions_map = {}
    _methods_map = {}

    def _map_perms(self, method):
        if self._action in self._actions_map:
            return self._actions_map[self._action]
        return self._methods_map[method]

    def _get_default_permissions(self, method, view):
        """
        Given a view and a HTTP method, return the list of permission
        codes that the user is required to have.
        """
        model_cls = view.get_bmfmodel()
        kwargs = {
            'app': model_cls._meta.app_label,
            'model': model_cls._meta.model_name,
        }
        return [perm % kwargs for perm in self._map_perms(method)]

    def has_permission(self, request, view):
        perms = self._get_default_permissions(request.method, view)
        return request.user.has_perms(perms)

    def has_module_permission(self, request, obj):
        return True

    def has_object_permission(self, request, view, obj):
        perms = self._get_default_permissions(request.method, view)

        if not self.has_module_permission(request, obj):
            return False

        if request.user.has_perms(perms, obj):
            return True

        # If the user does not have permissions we need to determine if
        # they have read permissions to see 403, or get a 404 response.

        if request.method in SAFE_METHODS:
            # Read permissions already checked and failed, no need
            # to make another lookup.
            raise Http404

        read_perms = self.get_permissions('GET', view)
        if not request.user.has_perms(read_perms, obj):
            raise Http404

        # Has read permissions - generate 403 response
        return False

    def filter_queryset(self, qs, user):
        return qs


class NotificationPermission(BaseModulePermission):
    _methods_map = {
        'GET': ['%(app)s.view_%(model)s'],
        'OPTIONS': ['%(app)s.view_%(model)s'],
        'HEAD': ['%(app)s.view_%(model)s'],
        'POST': ['%(app)s.view_%(model)s'],
    }


class ActivityPermission(BaseModulePermission):
    _methods_map = {
        'GET': ['%(app)s.view_%(model)s'],
        'OPTIONS': ['%(app)s.view_%(model)s'],
        'HEAD': ['%(app)s.view_%(model)s'],
        'POST': ['%(app)s.view_%(model)s', '%(app)s.comment_%(model)s'],
    }


class FilePermission(BaseModulePermission):
    _methods_map = {
        'GET': ['%(app)s.view_%(model)s'],
        'OPTIONS': ['%(app)s.view_%(model)s'],
        'HEAD': ['%(app)s.view_%(model)s'],
        'POST': ['%(app)s.view_%(model)s', '%(app)s.addfile_%(model)s'],
    }


class ModulePermission(BaseModulePermission):
    """
    Permission object to check the module's permissions
    """
    _actions_map = {
        'view': ['%(app)s.view_%(model)s'],
        'clone': ['%(app)s.view_%(model)s', '%(app)s.clone_%(model)s'],
        'create': ['%(app)s.view_%(model)s', '%(app)s.add_%(model)s'],
        'update': ['%(app)s.view_%(model)s', '%(app)s.change_%(model)s'],
        'delete': ['%(app)s.view_%(model)s', '%(app)s.delete_%(model)s'],
    }
    _methods_map = {
        'GET': ['%(app)s.view_%(model)s'],
        'OPTIONS': ['%(app)s.view_%(model)s'],
        'HEAD': ['%(app)s.view_%(model)s'],
        'POST': ['%(app)s.view_%(model)s', '%(app)s.add_%(model)s'],
        'PUT': ['%(app)s.view_%(model)s', '%(app)s.change_%(model)s'],
        'PATCH': ['%(app)s.view_%(model)s', '%(app)s.change_%(model)s'],
        'DELETE': ['%(app)s.view_%(model)s', '%(app)s.delete_%(model)s'],
    }

    def has_module_permission(self, request, obj):

        # generate a 403 response if the object's state does not allow it to be updated
        if request.method in ["PUT", "PATCH"] or self._action in ["update"]:
            if obj._bmfmeta.workflow and not obj._bmfmeta.workflow.object.update:
                return False

        # generate a 403 response if the object's state does not allow it to be deleted
        if request.method in ["DELETE"] or self._action in ["delete"]:
            if obj._bmfmeta.workflow and not obj._bmfmeta.workflow.object.delete:
                return False

        return True


class ModuleViewPermission(ModulePermission):
    _action = 'view'


class ModuleCreatePermission(ModulePermission):
    _action = 'create'


class ModuleClonePermission(ModulePermission):
    _action = 'clone'


class ModuleUpdatePermission(ModulePermission):
    _action = 'update'


class ModuleDeletePermission(ModulePermission):
    _action = 'delete'
