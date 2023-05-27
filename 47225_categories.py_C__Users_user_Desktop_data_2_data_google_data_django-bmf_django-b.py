#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from djangobmf.dashboards import ProjectManagement
from djangobmf.sites import Category


class ProjectCategory(Category):
    name = _('Projects')
    slug = "projects"
    dashboard = ProjectManagement
