#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.views.generic import TemplateView

from .module import ModuleCloneView
from .module import ModuleCreateView
from .module import ModuleDeleteView
from .module import ModuleDetail
from .module import ModuleFormAPI
from .module import ModuleReportView
from .module import ModuleUpdateView
from .module import ModuleWorkflowView

from .mixins import ModuleViewMixin
from .mixins import ViewMixin


__all__ = (
    'ModuleCloneView',
    'ModuleCreateView',
    'ModuleDeleteView',
    'ModuleDetail',
    'ModuleFormAPI',
    'ModuleReportView',
    'ModuleUpdateView',
    'ModuleWorkflowView',
    'ModuleViewMixin',
    'Index',
)


class Index(ViewMixin, TemplateView):
    template_name = "djangobmf/index.html"
