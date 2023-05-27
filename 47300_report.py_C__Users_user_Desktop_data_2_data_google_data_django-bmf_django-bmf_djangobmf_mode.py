#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
# from django.contrib.contenttypes.fields import GenericForeignKey
# from django.http import HttpResponse

# from djangobmf.core.report import Report as BaseReport
from djangobmf.models.renderer import Renderer


class Report(models.Model):
    """
    Model to store informations to generate a report
    """
    key = models.CharField(
        _("Key"),
        max_length=255,
        blank=True,
        null=True,
        editable=False,
        db_index=True,
    )
    contenttype = models.ForeignKey(
        ContentType, related_name="bmf_report", null=True, blank=True,
        help_text="Connect a Report to an BMF-Model", on_delete=models.CASCADE,
        editable=False,
    )
    renderer = models.ForeignKey(
        Renderer,
        related_name="reports",
        null=True,
        blank=True,
        help_text="Connect a Report to an Renderer",
        on_delete=models.SET_NULL,
    )
    modified = models.DateTimeField(_("Modified"), auto_now=True, editable=False,)

    class Meta:
        verbose_name = _('Report')
        verbose_name_plural = _('Reports')
        get_latest_by = "modified"
        abstract = True

    def __str__(self):
        return '%s' % self.key

#   def clean(self):
#       if self.options == "":
#           generator = self.get_generator()
#           self.options = generator.get_default_options().strip()

#   def get_generator(self):
#       from djangobmf.sites import site
#       try:
#           return site.reports[self.reporttype](self.options)
#       except KeyError:
#           return BaseReport()

    # response with generated file
    def render(self, filename, request, context):
        pass
#       generator = self.get_generator()

#       extension, mimetype, data, attachment = generator.render(request, context)

#       response = HttpResponse(content_type=mimetype)

#       if attachment:
#           response['Content-Disposition'] = 'attachment; filename="%s.%s"' % (
#               filename,
#               extension
#           )

#       response.write(data)

#       return response
