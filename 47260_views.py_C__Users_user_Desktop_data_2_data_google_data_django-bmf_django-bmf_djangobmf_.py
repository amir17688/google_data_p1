#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from djangobmf.views import ModuleCreateView
from djangobmf.views import ModuleUpdateView

from .forms import TeamUpdateForm
from .forms import TeamCreateForm


class TeamCreateView(ModuleCreateView):
    form_class = TeamCreateForm


class TeamUpdateView(ModuleUpdateView):
    form_class = TeamUpdateForm
