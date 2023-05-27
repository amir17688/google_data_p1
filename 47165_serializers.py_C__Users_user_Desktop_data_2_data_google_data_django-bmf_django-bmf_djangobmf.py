#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from djangobmf import fields

from rest_framework.fields import CharField
from rest_framework.fields import DecimalField
# from rest_framework.reverse import reverse
from rest_framework.serializers import ModelSerializer
# from rest_framework.serializers import SerializerMethodField


class ModuleSerializer(ModelSerializer):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ModuleSerializer, self).__init__(*args, **kwargs)

    def get_field_names(self, *args, **kwargs):
        names = super(ModuleSerializer, self).get_field_names(*args, **kwargs)

        if 'pk' not in names:
            names = ('pk',) + tuple(names)
        return names


class CountryField(CharField):
    def to_representation(self, value):
        return value.alpha3
ModuleSerializer.serializer_field_mapping[fields.CountryField] = CountryField


class MoneyField(DecimalField):
    def to_representation(self, value):
        return value.value
ModuleSerializer.serializer_field_mapping[fields.MoneyField] = MoneyField


class WorkflowField(CharField):
    def to_representation(self, value):
        return value.key
ModuleSerializer.serializer_field_mapping[fields.WorkflowField] = WorkflowField
