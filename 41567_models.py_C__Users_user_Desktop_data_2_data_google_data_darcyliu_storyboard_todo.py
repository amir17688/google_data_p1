#!/usr/bin/env python
# encoding: utf-8
"""
models.py

Created by Darcy Liu on 2012-03-03.
Copyright (c) 2012 Close To U. All rights reserved.
"""
from django.db import models
from django.contrib.auth.models import User

class Task(models.Model):
    title = models.CharField(max_length=256,verbose_name='title')
    description = models.TextField(blank=True, verbose_name='text')
    Status_Choices = (
            ('0', 'Todo'),
            ('1', 'Done'),
            ('2', 'Archive'),
            ('9', 'Trash'),
        )
    status = models.CharField(verbose_name='status',max_length=1,default=0,choices=Status_Choices)
    author = models.ForeignKey(User,verbose_name='author')
    created = models.DateTimeField(auto_now_add=True,verbose_name='created')
    updated = models.DateTimeField(auto_now=True,verbose_name='updated')
    def __unicode__(self):
        result = self.title
        return unicode(result)
