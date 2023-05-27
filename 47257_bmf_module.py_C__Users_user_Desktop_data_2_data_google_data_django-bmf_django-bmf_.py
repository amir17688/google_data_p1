#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from djangobmf.sites import Module
from djangobmf.sites import ViewMixin
from djangobmf.sites import register

from .categories import TeamCategory
from .models import Team
from .models import TeamMember
from .views import TeamCreateView
from .views import TeamUpdateView


@register
class TeamModule(Module):
    model = Team
    default = True
    create = TeamCreateView
    update = TeamUpdateView


@register
class TeamMemberModule(Module):
    model = TeamMember
    default = True


@register(category=TeamCategory)
class AllTeams(ViewMixin):
    model = Team
    name = _("All Teams")
    slug = "all"
