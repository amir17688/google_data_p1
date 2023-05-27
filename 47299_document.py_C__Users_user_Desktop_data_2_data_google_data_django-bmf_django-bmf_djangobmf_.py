#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from djangobmf.conf import settings as bmfsettings
from djangobmf.storage import default_storage
from djangobmf.tasks import generate_sha1
from djangobmf.utils.generate_filename import generate_filename


@python_2_unicode_compatible
class Document(models.Model):
    name = models.CharField(_('Name'), max_length=120, null=True, blank=True)
    mimetype = models.CharField(_('Mimetype'), max_length=120, editable=False, null=True)
    encoding = models.CharField(_('Encoding'), max_length=60, editable=False, null=True)
    description = models.TextField(_('Description'), blank=True, null=True)
    file = models.FileField(_('File'), upload_to=generate_filename, storage=default_storage)
    size = models.PositiveIntegerField(null=True, blank=True, editable=False)
    sha1 = models.CharField(_('SHA1'), max_length=40, editable=False, null=True)

    is_static = models.BooleanField(default=True, editable=False)
    file_exists = models.BooleanField(default=True)

    customer = models.ForeignKey(
        bmfsettings.CONTRIB_CUSTOMER,
        null=True,
        blank=True,
        related_name="documents",
        on_delete=models.SET_NULL,
        editable=False,
    )

    project = models.ForeignKey(
        bmfsettings.CONTRIB_PROJECT,
        null=True,
        blank=True,
        related_name="documents",
        on_delete=models.SET_NULL,
        editable=False,
    )

    content_type = models.ForeignKey(
        ContentType,
        related_name="bmf_document",
        null=True,
        blank=True,
        editable=False,
        on_delete=models.SET_NULL,
    )
    content_id = models.PositiveIntegerField(null=True, blank=True, editable=False)
    content_object = GenericForeignKey('content_type', 'content_id')

    modified = models.DateTimeField(_("Modified"), auto_now=True, editable=False, null=True, blank=False)
    created = models.DateTimeField(_("Created"), auto_now_add=True, editable=False, null=True, blank=False)
    modified_by = models.ForeignKey(
        getattr(settings, 'AUTH_USER_MODEL', 'auth.User'),
        null=True, blank=True, editable=False,
        related_name="+", on_delete=models.SET_NULL)
    created_by = models.ForeignKey(
        getattr(settings, 'AUTH_USER_MODEL', 'auth.User'),
        null=True, blank=True, editable=False,
        related_name="+", on_delete=models.SET_NULL)

    class Meta:
        verbose_name = _('Document')
        verbose_name_plural = _('Documents')
        get_latest_by = "modified"
        permissions = [('view_document', 'Can view documents')]
        abstract = True

    def __init__(self, *args, **kwargs):
        super(Document, self).__init__(*args, **kwargs)
        self.original_name = self.name

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.clean()
        super(Document, self).save(*args, **kwargs)
        generate_sha1(self.pk)

    def clean(self):

        name = self.file.name.split(r'/')[-1]
        if not self.name or self.original_name == self.name:
            self.name = name

        if hasattr(self.content_object, 'bmfget_project'):
            self.project = self.content_object.bmfget_project()

        if hasattr(self.content_object, 'bmfget_customer'):
            self.customer = self.content_object.bmfget_customer()
