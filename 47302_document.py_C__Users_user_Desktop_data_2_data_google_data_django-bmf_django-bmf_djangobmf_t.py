#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.utils import six

from djangobmf.decorators import optional_celery

import hashlib
import mimetypes


if six.PY2:
    class FileNotFoundError(OSError):
        pass


@optional_celery
def generate_sha1(pk):
    from djangobmf.models import Document

    obj = Document.objects.get(pk=pk)

    hash = hashlib.sha1()

    try:
        obj.file.open('rb')

        exists = True
        size = obj.file.size
        mimetype, encoding = mimetypes.guess_type(obj.file.name)

        if obj.file.multiple_chunks():
            for chunk in obj.file.chunks():
                hash.update(chunk)
        else:
            hash.update(obj.file.read())

        obj.file.close()

        sha1 = hash.hexdigest()

    except FileNotFoundError:
        exists = False
        size = None
        mimetype = None
        encoding = None
        sha1 = None

    if sha1 != obj.sha1 or exists != obj.file_exists or mimetype != obj.mimetype \
            or encoding != obj.encoding or size != obj.size:

        Document.objects.filter(pk=pk).update(
            sha1=sha1,
            file_exists=exists,
            mimetype=mimetype,
            encoding=encoding,
            size=size,
        )
