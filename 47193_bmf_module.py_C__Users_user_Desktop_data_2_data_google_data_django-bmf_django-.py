#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from djangobmf.sites import Module
from djangobmf.sites import ViewMixin
from djangobmf.sites import register

from .categories import EmployeeCategory
from .models import Employee
from .views import EmployeeCreateView


@register
class EmployeeModule(Module):
    model = Employee
    default = True
    create = EmployeeCreateView


@register(category=EmployeeCategory)
class AllAccounts(ViewMixin):
    model = Employee
    name = _("All Employees")
    slug = "all"
