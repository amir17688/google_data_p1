#!/usr/bin/env python
# encoding: utf-8
"""
views.py

Created by Darcy Liu on 2012-04-02.
Copyright (c) 2012 Close To U. All rights reserved.
"""
import datetime
import logging
import hashlib

from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.contrib import auth

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseNotModified
from django.http import HttpResponseNotFound

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm

from django.utils import simplejson

# from google.appengine.api import files
from config import STORAGE_SERVICE,STORAGE_BUCKET,STORAGE_FOLDER,STORAGE_ACCESS_KEY,STORAGE_SECRET_ACCESS_KEY

from models import *
from forms import *

import tempfile
import boto
import logging
logger = logging.getLogger(__name__)
# from google.appengine.api import images

# config = boto.config
# config.add_section('Credentials')
# config.set('Credentials', 'gs_access_key_id', '')
# config.set('Credentials', 'gs_secret_access_key', '')

def photos(request):
    query = Storage.objects.all().order_by('-updated').filter(kind='image')
    return render_to_response('storage/photos.html',{'photos':query},context_instance=RequestContext(request))

@login_required
def ajax_upload(request):
    if request.method == 'POST':
        name = request.META['HTTP_X_FILE_NAME']
        content_type = request.META['HTTP_CONTENT_TYPE'] or 'application/octet-stream'
        file_size = request.META['HTTP_X_FILE_SIZE']
        file_data  = request.raw_post_data
        
        # logging.info(request.META.keys())
        # logging.info(name)
        # logging.info(content_type)
        # logging.info(file_size)
        
        if file_size>0 and file_data:
            now = datetime.datetime.now()

            file_ext_pos = name.rfind('.')
            file_name_len = len(name)

            if not (content_type == 'image/jpeg' or content_type == 'image/png' or content_type == 'image/gif'):
                return
            if file_ext_pos<=0 and file_ext_pos>=file_name_len:
                return
            file_ext = name[file_ext_pos-file_name_len:]                
            file_name = 'uploads/ohbug/photo/%s%s' % (now.strftime('%Y-%m/%d-%H%M%S-%f'),file_ext)
            file_path = '/%s/%s/%s' % (STORAGE_SERVICE,STORAGE_BUCKET,file_name)
            #logging.info(file_path)
            
            write_path = files.gs.create(file_path, acl='bucket-owner-full-control',mime_type=content_type)
            with files.open(write_path, 'a') as fp:
                fp.write(file_data)
            files.finalize(write_path)
            s = Storage()
            s.storage  = STORAGE_SERVICE
            s.bucket  = STORAGE_BUCKET
            s.path = file_name
            s.mime = content_type
            s.size = len(file_data)
            s.md5 = hashlib.md5(file_data).hexdigest()
            s.name = name
            s.author = request.user
            s.save()
            
            HTTP_HOST = request.META['HTTP_HOST']
            to_json = {
                'origin': 'http://%s/photo/%s' % (HTTP_HOST,s.key) ,
                'url': 'http://%s/photo/raw/%s.%s' % (HTTP_HOST,s.key,s.name)
            }
            return HttpResponse(simplejson.dumps(to_json), mimetype='application/json')
    else:
        #return HttpResponse('ajax_upload: POST method required.')
        return HttpResponseRedirect('/photo/upload')

@login_required      
def upload(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            if request.FILES.has_key('images'):
                name = request.FILES['images'].name
                content_type = request.FILES['images'].content_type or 'application/octet-stream'#'text/plain'
                file_data = request.FILES['images'].read()
                
                now = datetime.datetime.now()

                file_ext_pos = name.rfind('.')
                file_name_len = len(name)

                if not (content_type == 'image/jpeg' or content_type == 'image/png' or content_type == 'image/gif'):
                    return
                if file_ext_pos<=0 and file_ext_pos>=file_name_len:
                    return
                file_ext = name[file_ext_pos-file_name_len:].lower()
                file_uri  = '%s%s' % (now.strftime('%Y-%m-%d-%H%M%S-%f'),file_ext)          
                file_name = 'uploads/ohbug/photo/%s%s' % (now.strftime('%Y-%m/%d-%H%M%S-%f'),file_ext)
                file_path = '/%s/%s/%s' % (STORAGE_SERVICE,STORAGE_BUCKET,file_name)

                if STORAGE_SERVICE == 'sina':
                    import sae.storage
                    s = sae.storage.Client()
                    ob = sae.storage.Object(file_data,expires='', content_type=content_type, content_encoding='gzip')
                    s.put(STORAGE_BUCKET, file_uri , ob)
                    file_name = file_uri

                if STORAGE_SERVICE == 'baidu':
                    # TMPDIR = '/tmp'
                    # try:
                    #     from bae.core import const
                    #     TMPDIR = const.APP_TMPDIR
                    # except Exception, e:
                    #     pass
                    # output = open(TMPDIR+'/'+file_uri, 'wb')
                    # output.write(file_data)
                    # output.close()
                    # try:
                    #   from bae.api import logging as logger
                    # except:
                    #   import logging
                    #   logger = logging.getLogger('pyhttpclient')
                    # logger.info('file_data')
                    # logger.info(file_uri)
                    # BAE API
                    # from bae.api import bcs
                    # baebcs = bcs.BaeBCS('http://bcs.duapp.com/', STORAGE_ACCESS_KEY, STORAGE_SECRET_ACCESS_KEY)
                    # #obj_path = TMPDIR+'/'+file_uri
                    # obj_name = u'/%s'%(file_uri)
                    # baebcs.put_object(STORAGE_BUCKET, obj_name.encode('utf8'), file_data)
                    # #baebcs.put_file(STORAGE_BUCKET, obj_name.encode('utf8'), obj_path.encode('utf8'))
                    # baebcs.make_public(STORAGE_BUCKET, obj_name.encode('utf8'))

                    # BCS API
                    import pybcs
                    # # TMPDIR = '/tmp'
                    # # try:
                    # #     from bae.core import const
                    # #     TMPDIR = const.APP_TMPDIR
                    # # except Exception, e:
                    # #     pass
                    # # output = open(TMPDIR+'/'+file_uri, 'wb')
                    # # output.write(file_data)
                    # # output.close()
                    bcs = pybcs.BCS('http://bcs.duapp.com/', STORAGE_ACCESS_KEY, STORAGE_SECRET_ACCESS_KEY)
                    bucket = bcs.bucket(STORAGE_BUCKET)
                    obj_name = u'/%s'%(file_uri)
                    obj = bucket.object(obj_name.encode('utf8'))
                    obj.put(file_data)
                    obj.make_public()
                    #obj.put_file(TMPDIR+'/'+file_uri)
                    file_name = file_uri

                # Google Storage
                if STORAGE_SERVICE == 'gs':
                    dst_uri = boto.storage_uri(STORAGE_BUCKET, STORAGE_SERVICE)
                    
                    new_dst_uri = dst_uri.clone_replace_name(file_name)
                    #logging.info(dst_uri)
                    #logging.info(new_dst_uri)
                    tmp = tempfile.TemporaryFile()
                    tmp.write(file_data)
                    tmp.seek(0)
                    dst_key = new_dst_uri.new_key()
                    dst_key.content_type = content_type
                    dst_key.set_contents_from_file(tmp)
                    #logger.info('hello')
                    
                    # write_path = files.gs.create(file_path, acl='bucket-owner-full-control',mime_type=content_type)
                    # with files.open(write_path, 'a') as fp:
                    #     fp.write(file_data)
                    # files.finalize(write_path)

                s = Storage()
                s.storage  = STORAGE_SERVICE
                s.bucket  = STORAGE_BUCKET
                s.path = file_name
                s.mime = content_type
                s.size = len(file_data)
                s.md5 = hashlib.md5(file_data).hexdigest()
                s.name = name
                s.kind = 'image'
                s.author = request.user
                s.save()
                return HttpResponseRedirect('/photo/%s'%s.key)
    else:
        form = UploadForm()
    return render_to_response('storage/upload.html',{'form':form},context_instance=RequestContext(request))
    
def view(request,key=None):
    s = get_object_or_404(Storage,pk=key)
    # name = s.name
    # file_ext_pos = name.rfind('.')
    # file_name_len = len(name)
    # file_ext = name[file_ext_pos-file_name_len:]
    HTTP_HOST = request.META['HTTP_HOST']
    url = 'http://%s/photo/raw/%s.%s' % (HTTP_HOST,s.key,s.name)
    if STORAGE_SERVICE == 'baidu':
        url = 'http://bcs.duapp.com/%s/%s'%(STORAGE_BUCKET,s.path)
    image = {
        'origin': s,
        'url': url
    }
    return render_to_response('storage/photo.html',{'image':image},context_instance=RequestContext(request))
    
def read_gs(read_path):
    image_data = None
    try:
        with files.open(read_path, 'r') as fp:
            buf = fp.read(1000000)
            image_data = buf
            while buf:
                buf = fp.read(1000000)
                image_data +=buf
    except Exception,e:
        pass
    return image_data

def cache_response(new_image, mime):
    response = HttpResponse(new_image, mime)
    format_str = '%a, %d %b %Y %H:%M:%S GMT'
    expires_date = datetime.datetime.utcnow() + datetime.timedelta(365)
    expires_str = expires_date.strftime(format_str)
    last_modified_date = datetime.datetime.utcnow()
    last_modified_str = expires_date.strftime(format_str)
    response['Expires'] = expires_str #eg:'Sun, 08 Apr 2013 11:11:02 GMT'
    response["Last-Modified"] = last_modified_str #for 'If-Modified-Since'
    response['Cache-Control'] = 'max-age=172800'
    #response['Content-Disposition'] = 'attachment; filename=%s' % s.name
    #response["ETag"] = ''
    return  response
              
def raw(request,key=None):
    if request.META.has_key('HTTP_IF_MODIFIED_SINCE'):
        return HttpResponseNotModified()
    #request.META.get("HTTP_IF_NONE_MATCH", None)    
    s = get_object_or_404(Storage,pk=key)
    #read_path =  '/%s/%s/%s'% (s.storage, s.bucket, s.path)
    #image_data = read_gs(read_path)
    tmp = None

    if STORAGE_SERVICE == 'sina':
        import sae.storage
        sc = sae.storage.Client()
        ob = sc.get(STORAGE_BUCKET, s.path)
        url = sc.url(STORAGE_BUCKET, s.path)
        print url
        if ob and ob.data:
            tmp = ob.data

    if STORAGE_SERVICE == 'baidu':
        import pybcs
        bcs = pybcs.BCS('http://bcs.duapp.com/', STORAGE_ACCESS_KEY, STORAGE_SECRET_ACCESS_KEY)
        bucket = bcs.bucket(STORAGE_BUCKET)
        obj_name = u'/%s'%(s.path)
        obj = bucket.object(obj_name.encode('utf8'))
        tmp = obj.get()['body']

    if STORAGE_SERVICE == 'gs':
        src_uri = boto.storage_uri(s.bucket + '/' + s.path, 'gs')
        src_key = src_uri.get_key()
        tmp = tempfile.TemporaryFile()
        src_key.get_file(tmp)
        tmp.seek(0)
    
    if tmp:
        return cache_response(tmp, s.mime)
    else:
        return HttpResponseNotFound()
    
def thumbnail(request,key=None):
    if request.META.has_key('HTTP_IF_MODIFIED_SINCE'):
        return HttpResponseNotModified()
    s = get_object_or_404(Storage,pk=key)
    image_data = None

    if STORAGE_SERVICE == 'sina':
        import sae.storage
        sc = sae.storage.Client()
        ob = sc.get(STORAGE_BUCKET, s.path)
        if ob and ob.data:
            image_data = ob.data

    if STORAGE_SERVICE == 'baidu':
        import pybcs
        bcs = pybcs.BCS('http://bcs.duapp.com/', STORAGE_ACCESS_KEY, STORAGE_SECRET_ACCESS_KEY)
        bucket = bcs.bucket(STORAGE_BUCKET)
        obj_name = u'/%s'%(s.path)
        obj = bucket.object(obj_name.encode('utf8'))
        image_data = obj.get()['body']

    if STORAGE_SERVICE == 'gs':
        read_path =  '/%s/%s/%s'% (s.storage, s.bucket, s.path)
        #image_data = read_gs(read_path)
        src_uri = boto.storage_uri(s.bucket + '/' + s.path, 'gs')
        src_key = src_uri.get_key()
        tmp = tempfile.TemporaryFile()
        src_key.get_file(tmp)
        tmp.seek(0)
        image_data = tmp
        image_data = tmp.read()
    
    if image_data:
        # MIN_SIZE = 100
        # image = images.Image(image_data)
        # width = image.width
        # height = image.height
        # if width>height:
        #     rate = width*1.0/height
        # else:
        #     rate = height*1.0/width
        # size = int(MIN_SIZE*rate+1)
        # new_image = images.resize(image_data, width=size, height=size, output_encoding=images.PNG)      
        # image = images.Image(new_image)
        # right_x = round(MIN_SIZE*1.0/image.width,5)
        # if right_x>1:
        #     right_x = 1.0
        # else:
        #     left_x = (1- right_x)/2
        #     right_x = right_x + left_x
        # bottom_y = round(MIN_SIZE*1.0/image.height,5)
        # if bottom_y >1:
        #     bottom_y = 1.0
        # else:
        #     top_y = (1-bottom_y)/2
        #     bottom_y = bottom_y + top_y
        # new_image = images.crop(new_image, left_x, top_y, right_x, bottom_y, output_encoding=images.PNG)
        #return cache_response(image_data, s.mime)
        from PIL import Image,ImageOps
        import StringIO
        img = Image.open(StringIO.StringIO(image_data))
        #region = img.resize((100, 100),Image.ANTIALIAS)
        region = ImageOps.fit(img,(100, 100),Image.ANTIALIAS)
        response = HttpResponse(mimetype="image/png")
        format_str = '%a, %d %b %Y %H:%M:%S GMT'
        expires_date = datetime.datetime.utcnow() + datetime.timedelta(365)
        expires_str = expires_date.strftime(format_str)
        last_modified_date = datetime.datetime.utcnow()
        last_modified_str = expires_date.strftime(format_str)
        response['Expires'] = expires_str #eg:'Sun, 08 Apr 2013 11:11:02 GMT'
        response["Last-Modified"] = last_modified_str #for 'If-Modified-Since'
        response['Cache-Control'] = 'max-age=172800'
        
        region.save(response, 'PNG', quality = 100)
        return response
    else:
        return HttpResponseNotFound()