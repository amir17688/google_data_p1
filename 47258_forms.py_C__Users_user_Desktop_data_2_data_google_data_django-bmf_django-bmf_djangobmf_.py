#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.forms import ModelForm

from .models import Team
# from .models import TeamMember


class TeamUpdateForm(ModelForm):
    class Meta:
        model = Team
        exclude = []


class TeamCreateForm(ModelForm):
    class Meta:
        model = Team
        exclude = []
