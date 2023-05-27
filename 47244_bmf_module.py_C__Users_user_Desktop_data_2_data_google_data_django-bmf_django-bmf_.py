#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from djangobmf.sites import Relationship
from djangobmf.sites import Module
from djangobmf.sites import ViewMixin
from djangobmf.sites import register

from .categories import GoalCategory
from .categories import TaskCategory
from .models import Task
from .models import Goal
# from .permissions import GoalPermission
# from .permissions import TaskPermission
from .views import GoalDetailView
from .views import GoalCloneView


@register
class TaskModule(Module):
    model = Task
    default = True


@register
class GoalModule(Module):
    model = Goal
    default = True
    clone = GoalCloneView
    detail = GoalDetailView


@register(model=Task)
class ProjectTaskRelationship(Relationship):
    name = _("Open Tasks")
    slug = "task"
    field = "task_set"
    model = "djangobmf_project.Project"
    settings = "BMF_CONTRIB_PROJECT"
    template = "djangobmf_task/task_related_project.html"

    def filter_queryset(self, request, queryset, view):
        return queryset.filter(
            completed=False,
        )


@register(model=Goal)
class ProjectGoalRelationship(Relationship):
    name = _("Active Goals")
    slug = "goal"
    field = "goal_set"
    model = "djangobmf_project.Project"
    settings = "BMF_CONTRIB_PROJECT"
    template = "djangobmf_task/goal_related_project.html"

    def filter_queryset(self, request, queryset, view):
        return queryset.filter(
            completed=False,
        )


@register(model=Task)
class GoalTasksRelationship(Relationship):
    name = _("Tasks")
    slug = "task"
    field = "task_set"
    model = "djangobmf_task.Goal"
    settings = "BMF_CONTRIB_GOAL"
    template = "djangobmf_task/task_related_goal.html"


@register(category=GoalCategory)
class MyGoals(ViewMixin):
    model = Goal
    slug = 'my'
    name = _("My goals")

    def filter_queryset(self, request, queryset, view):
        return queryset.filter(
            completed=False,
            referee=request.user.djangobmf.employee,
        )


@register(category=GoalCategory)
class ActiveGoals(ViewMixin):
    model = Goal
    slug = 'active'
    name = _("Active goals")

    def filter_queryset(self, request, queryset, view):
        return queryset.filter(
            completed=False,
        )


@register(category=GoalCategory)
class ArchiveGoals(ViewMixin):
    model = Goal
    slug = 'archive'
    name = _("Archive")


@register(category=TaskCategory)
class MyTasks(ViewMixin):
    model = Task
    slug = 'my'
    name = _("My tasks")

    def filter_queryset(self, request, queryset, view):
        return queryset.filter(
            completed=False,
            employee=request.user.djangobmf.employee,
        )


@register(category=TaskCategory)
class Todolist(ViewMixin):
    model = Task
    slug = 'todo'
    name = _("Todolist")

    def filter_queryset(self, request, queryset, view):
        return queryset.filter(
            completed=False,
            state__in=["todo", "started", "review"],
            employee=request.user.djangobmf.employee,
        )


@register(category=TaskCategory)
class AvailableTasks(ViewMixin):
    model = Task
    slug = 'availiable'
    name = _("Availalbe tasks")

    def filter_queryset(self, request, queryset, view):
        return queryset.filter(
            employee=None,
            completed=False,
        )


@register(category=TaskCategory)
class OpenTasks(ViewMixin):
    model = Task
    slug = 'open'
    name = _("Open tasks")

    def filter_queryset(self, request, queryset, view):
        return queryset.filter(
            completed=False,
        )


@register(category=TaskCategory)
class ArchiveTasks(ViewMixin):
    model = Task
    slug = 'archive'
    name = _("Archive")

    def filter_queryset(self, request, queryset, view):
        return queryset.order_by('-modified')
