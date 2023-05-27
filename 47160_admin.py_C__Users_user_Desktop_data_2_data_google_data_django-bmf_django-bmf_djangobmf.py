#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.contrib import admin

from djangobmf.models import Configuration
from djangobmf.models import Document
from djangobmf.models import Report
from djangobmf.models import Renderer


admin.site.register(Configuration)
admin.site.register(Report)
admin.site.register(Renderer)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'mimetype', 'size', 'sha1', 'is_static', 'content_type')
    list_display_links = ('name',)
    list_filter = ('modified', 'content_type', 'is_static')
    search_fields = ['name', 'description']
