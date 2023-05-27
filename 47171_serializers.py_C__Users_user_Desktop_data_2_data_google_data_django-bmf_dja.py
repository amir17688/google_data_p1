#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.utils.formats import date_format

from djangobmf.serializers import ModuleSerializer

from rest_framework import serializers


class AccountSerializer(ModuleSerializer):
    balance_formatted = serializers.SerializerMethodField()
    type_name = serializers.SerializerMethodField()

    class Meta:
        fields = [
            'parent', 'number', 'name', 'balance', 'balance_currency',
            'balance_formatted', 'type_name',
        ]

    def get_balance_formatted(self, obj):
        return '%s' % obj.balance

    def get_type_name(self, obj):
        return '%s' % obj.get_type_display()


class TransactionSerializer(ModuleSerializer):
    class Meta:
        fields = ['text', 'project']


class TransactionItemSerializer(ModuleSerializer):
    transaction_name = serializers.SerializerMethodField()
    account_name = serializers.SerializerMethodField()
    date_localized = serializers.SerializerMethodField()

    class Meta:
        fields = [
            'date', 'credit', 'amount', 'amount_currency', 'account_name',
            'transaction_name', 'date_localized'
        ]

    def get_account_name(self, obj):
        return '%s' % obj.account

    def get_transaction_name(self, obj):
        return '%s' % obj.transaction

    def get_date_localized(self, obj):
        return date_format(obj.date, "SHORT_DATE_FORMAT")
