#!/usr/bin/env python
# encoding: utf-8
"""
models.py

Created by Darcy Liu on 2012-04-02.
Copyright (c) 2012 Close To U. All rights reserved.
"""

from django.db import models
from django.contrib.auth.models import User

class Storage(models.Model):
    key = models.AutoField(primary_key=True)
    storage = models.CharField(max_length=64,verbose_name='name')
    bucket = models.CharField(max_length=64,verbose_name='bucket')
    path = models.CharField(max_length=256,verbose_name='path')
    name = models.CharField(max_length=256,verbose_name='name')
    mime = models.CharField(max_length=64,verbose_name='mime')
    size = models.IntegerField(default=0,verbose_name='size')
    md5 = models.CharField(max_length=32,verbose_name='md5')
    MEDIA_CHOICES = (
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('unknown', 'Unknown'),
    )
    kind = models.CharField(max_length=16,choices=MEDIA_CHOICES,default='unknown')
    public = models.BooleanField(default=False,verbose_name='public')
    author = models.ForeignKey(User,verbose_name='author')
    created = models.DateTimeField(auto_now_add=True,verbose_name='created')
    updated = models.DateTimeField(auto_now=True,verbose_name='updated')
    def __unicode__(self):
        result = self.name + self.path
        return unicode(result)

# class Media(models.Model):
#     key = models.AutoField(primary_key=True)
#     kind = models.CharField(max_length=64,verbose_name='kind')
#     pv = models.IntegerField(default=0,verbose_name='pv')
#     comments = models.IntegerField(default=0,verbose_name='comments')
#     entity = models.ForeignKey(Storage,verbose_name='storage')
#     author = models.ForeignKey(User,verbose_name='author')
#     created = models.DateTimeField(auto_now_add=True,verbose_name='created')
#     updated = models.DateTimeField(auto_now=True,verbose_name='updated')
#     def __unicode__(self):
#         result = self.kind + '/'
#         return unicode(result)