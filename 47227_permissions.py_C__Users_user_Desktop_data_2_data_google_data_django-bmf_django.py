#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.db.models import Q

from djangobmf.permissions import ModulePermission


class ProjectPermission(ModulePermission):

    def filter_queryset(self, qs, user):
        if user.has_perm('%s.can_manage' % qs.model._meta.app_label, qs.model):
            return qs
        return qs.filter(
            Q(employees=user.djangobmf.employee or -1) |
            Q(team__in=user.djangobmf.teams)
        )
