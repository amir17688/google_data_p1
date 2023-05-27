#!/usr/bin/env python
# encoding: utf-8
"""
views.py

Created by Darcy Liu on 2012-03-03.
Copyright (c) 2012 Close To U. All rights reserved.
"""
import logging
from django.views.generic import TemplateView
from django.views.generic import ListView
from django.views.generic import DetailView

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from models import *

class TodoEntryListView(ListView):
	context_object_name = "entries"
	template_name = "todo/todo.html"
	def get_queryset(self):
		entries = Task.objects.all()
		return entries
	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):        
		return super(ListView, self).dispatch(request, *args, **kwargs)