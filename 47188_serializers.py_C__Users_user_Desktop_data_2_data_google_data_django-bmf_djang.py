#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from djangobmf.serializers import ModuleSerializer

from rest_framework import serializers


class CustomerSerializer(ModuleSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    employee = serializers.ReadOnlyField(source='employee_at.name')

    class Meta:
        fields = (
            'number',
            'name',
            'username',
            'employee',
            'employee_at',
            'is_company',
            'is_active',
            'is_customer',
            'is_supplier',
        )
