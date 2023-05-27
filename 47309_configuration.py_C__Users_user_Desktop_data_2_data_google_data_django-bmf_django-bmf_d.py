#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django import forms
from django.core.urlresolvers import reverse
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.views.generic import ListView
from django.views.generic import FormView

from djangobmf.views.mixins import ViewMixin
from djangobmf.models import Configuration
from djangobmf.sites import site

import json


class ConfigurationView(ViewMixin, ListView):
    model = Configuration
    template_name = "djangobmf/configuration/index.html"


class ConfigurationEdit(ViewMixin, FormView):
    template_name = "djangobmf/configuration/edit.html"

    def get_form_class(self):
        app_label = self.kwargs['app_label']
        name = self.kwargs['name']

        class ConfigForm(forms.Form):
            """
            dynamic generated form with all settings
            """
            def __init__(self, *args, **kwargs):
                super(ConfigForm, self).__init__(*args, **kwargs)
                self.fields[name] = site.get_setting_field(app_label, name)
        return ConfigForm

    def get_form(self, *args, **kwargs):
        form = super(ConfigurationEdit, self).get_form(*args, **kwargs)
        # update initial data
        form.fields[self.kwargs['name']].initial = Configuration.get_setting(
            self.kwargs['app_label'],
            self.kwargs['name'],
        )
        return form

    def form_valid(self, form, *args, **kwargs):
        obj, created = Configuration.objects.get_or_create(
            app_label=self.kwargs['app_label'],
            field_name=self.kwargs['name'],
        )
        value = form.cleaned_data[self.kwargs['name']]
        # data = {
        #     'type': None,
        #     'value': value,
        # }
        # if isinstance(value, models.Model):
        #     data['type'] = 'object'
        #     data['value'] = value.pk
        # obj.value = json.dumps(data, cls=DjangoJSONEncoder)
        if isinstance(value, models.Model):
            value = value.pk
        obj.value = json.dumps(value, cls=DjangoJSONEncoder)
        obj.save()
        return super(ConfigurationEdit, self).form_valid(form, *args, **kwargs)

    def get_success_url(self):
        return reverse('djangobmf:configuration')
