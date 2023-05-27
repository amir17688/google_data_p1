#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from djangobmf.serializers import ModuleSerializer

from rest_framework import serializers


class AddressSerializer(ModuleSerializer):
    name = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'name',
            'customer_name',
            'is_active',
            'is_billing',
            'is_shipping',
            'default_billing',
            'default_shipping',
        )

    def get_name(self, obj):
        return '%s' % obj

    def get_customer_name(self, obj):
        return '%s' % obj.customer
