#!/usr/bin/env python
# encoding: utf-8
"""
models.py

Created by Darcy Liu on 2012-03-03.
Copyright (c) 2012 Close To U. All rights reserved.
"""

from django.db import models
from django.contrib.auth.models import User

# class Setting(models.Model):
#     sid = models.AutoField(primary_key=True)
#     option = models.CharField(unique=True,max_length=128,verbose_name='Option')
#     value = models.CharField(max_length=256,verbose_name='Value')

class Minisite(models.Model):
    key = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256,verbose_name='name')
    slug = models.CharField(unique=True,max_length=128,verbose_name='slug')
    meta = models.TextField(blank=True, verbose_name='meta')
    description = models.TextField(blank=True, verbose_name='description')
    author = models.ForeignKey(User,verbose_name='author')
    created = models.DateTimeField(auto_now_add=True,verbose_name='created')
    updated = models.DateTimeField(auto_now=True,verbose_name='updated')
    def __unicode__(self):
        result = self.name
        return unicode(result)
        
class Page(models.Model):
    key = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256,verbose_name='name')
    slug = models.CharField(max_length=128,verbose_name='slug')
    #type=//insite standlone
    Mode_Choices = (
            ('0', 'insite'),
            ('1', 'standlone'),
        )
    mode = models.CharField(verbose_name='format',max_length=1,default=0,choices=Mode_Choices)
    #content-type
    
    mime = models.CharField(max_length=64,default='text/html;charset=utf-8',verbose_name='mime')
    #format
    Format_Choices = (
            ('0', 'txt'),
            ('1', 'html'),
            ('2', 'markdown'),
            ('3', 'textile'),
        )
    format = models.CharField(verbose_name='format',max_length=1,default=0,choices=Format_Choices)
    text = models.TextField(blank=True, verbose_name='content')
    script = models.TextField(blank=True, verbose_name='script')
    style = models.TextField(blank=True, verbose_name='style')
    text_html = models.TextField(blank=True, verbose_name='html')
    minisite = models.ForeignKey(Minisite,verbose_name='minisite')
    author = models.ForeignKey(User,verbose_name='author')
    created = models.DateTimeField(auto_now_add=True,verbose_name='created')
    updated = models.DateTimeField(auto_now=True,verbose_name='updated')
    def __unicode__(self):
        result = self.name
        return unicode(result)
    class Meta:
        unique_together = (('slug', 'minisite'),)