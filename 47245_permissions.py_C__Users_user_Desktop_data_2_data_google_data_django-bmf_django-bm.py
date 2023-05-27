#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.db.models import Q

# from djangobmf.permissions import ModulePermission
from djangobmf.utils import FilterQueryset


class GoalFilter(FilterQueryset):

    def filter_queryset(self, qs, user):
        if user.has_perm('%s.can_manage' % qs.model._meta.app_label, qs.model):
            return qs

        qs_filter = Q(referee=user.djangobmf.employee or -1)
        qs_filter |= Q(employees=user.djangobmf.employee or -1)
        qs_filter |= Q(team__in=user.djangobmf.team)

        if hasattr(qs.model, "project"):  # pragma: no branch
            project = qs.model._meta.get_field_by_name("project")[0].model
            if user.has_perm('%s.can_manage' % project._meta.app_label, project):
                qs_filter |= Q(project__isnull=False)
            else:
                qs_filter |= Q(project__isnull=False, project__employees=user.djangobmf.employee or -1)
                qs_filter |= Q(project__isnull=False, project__team__in=user.djangobmf.team)
        return qs.filter(qs_filter)


class TaskFilter(FilterQueryset):

    def filter_queryset(self, qs, user):
        qs_filter = Q(project__isnull=True, goal__isnull=True)
        qs_filter |= Q(employee=user.djangobmf.employee or -1)
        qs_filter |= Q(in_charge=user.djangobmf.employee)

        if hasattr(qs.model, "goal"):  # pragma: no branch
            goal = qs.model._meta.get_field_by_name("goal")[0].model
            if user.has_perm('%s.can_manage' % goal._meta.app_label, goal):
                qs_filter |= Q(goal__isnull=False)
            else:
                qs_filter |= Q(goal__isnull=False, goal__referee=user.djangobmf.employee or -1)
                qs_filter |= Q(goal__isnull=False, goal__employees=user.djangobmf.employee or -1)
                qs_filter |= Q(goal__isnull=False, goal__team__in=user.djangobmf.team)

        if hasattr(qs.model, "project"):  # pragma: no branch
            project = qs.model._meta.get_field_by_name("project")[0].model
            if user.has_perm('%s.can_manage' % project._meta.app_label, project):
                qs_filter |= Q(project__isnull=False)
            else:
                qs_filter |= Q(project__isnull=False, project__employees=user.djangobmf.employee or -1)
                qs_filter |= Q(project__isnull=False, project__team__in=user.djangobmf.team)

        return qs.filter(qs_filter)
