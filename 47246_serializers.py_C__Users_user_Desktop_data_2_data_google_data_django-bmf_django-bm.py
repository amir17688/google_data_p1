#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.utils.formats import date_format

from djangobmf.serializers import ModuleSerializer

from rest_framework import serializers


class GoalSerializer(ModuleSerializer):
    project_name = serializers.ReadOnlyField(source='project.name')
    state_name = serializers.ReadOnlyField(source='state.name')
    referee_name = serializers.ReadOnlyField(source='referee.name')
    state_summary = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'completed',
            'summary',
            'referee',
            'referee_name',
            'project',
            'project_name',
            'state',
            'state_name',
            'state_summary',
        )

    def get_state_summary(self, obj):
        return obj.get_states()


class TaskSerializer(ModuleSerializer):
    state_name = serializers.ReadOnlyField(source='state.name')
    project_name = serializers.ReadOnlyField(source='project.name')
    employee_name = serializers.ReadOnlyField(source='employee.name')
    goal_summary = serializers.ReadOnlyField(source='goal.summary')
    modified_date = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'state',
            'state_name',
            'summary',
            'completed',
            'project',
            'project_name',
            'goal',
            'goal_summary',
            'employee',
            'employee_name',
            'due_date',
            'modified',
            'modified_date',
        )

    def get_modified_date(self, obj):
        return date_format(obj.modified, "SHORT_DATE_FORMAT")
