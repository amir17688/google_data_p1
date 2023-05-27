from __future__ import absolute_import

from django.contrib import admin
from .models import Category, Metric, Datum

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'position')
    list_editable = ('position',)
    ordering = ('position',)

admin.site.register(Category, CategoryAdmin)

class MetricAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'position', 'show_on_dashboard', 'show_sparkline', 'period')
    list_editable = ('show_on_dashboard', 'category', 'position', 'show_sparkline', 'period')
    ordering = ('category__position', 'position')
    prepopulated_fields = {'slug': ['name']}

for MC in Metric.__subclasses__():
    admin.site.register(MC, MetricAdmin)

admin.site.register(Datum,
    list_display = ('timestamp', 'metric', 'measurement'),
)
