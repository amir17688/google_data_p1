#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from djangobmf.dashboards import HumanResources
from djangobmf.sites import Category


class EmployeeCategory(Category):
    name = _('Employees')
    slug = "employees"
    dashboard = HumanResources
