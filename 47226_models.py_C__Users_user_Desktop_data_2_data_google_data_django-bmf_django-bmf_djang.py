#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible

from djangobmf.conf import settings
from djangobmf.models import BMFModel

from .serializers import ProjectSerializer


@python_2_unicode_compatible
class BaseProject(BMFModel):
    team = models.ForeignKey(
        settings.CONTRIB_TEAM, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="bmf_projects",
    )
    employees = models.ManyToManyField(
        settings.CONTRIB_EMPLOYEE, blank=True,
        related_name="bmf_projects",
    )

    name = models.CharField(_("Name"), max_length=255, null=False, blank=False, editable=True, )
    is_active = models.BooleanField(_("Is active"), null=False, blank=True, default=True)

    class Meta:  # only needed for abstract models
        verbose_name = _('Project')
        verbose_name_plural = _('Projects')
        ordering = ['name']
        abstract = True
        permissions = (
            ('can_manage', 'Can manage all projects'),
        )
        swappable = "BMF_CONTRIB_PROJECT"

    def __str__(self):
        return self.name

    def bmfget_project(self):
        return self

    # TODO add validations and make it impossible that you can create a project which is hidden to yourself


class AbstractProject(BaseProject):
    """
    """
    notes = models.TextField(null=False, blank=True, )

    customer = models.ForeignKey(  # TODO: make optional
        settings.CONTRIB_CUSTOMER, null=True, blank=True, related_name="bmf_projects",
        on_delete=models.SET_NULL,
    )

    def bmfget_customer(self):
        return self.customer

    class Meta(BaseProject.Meta):
        abstract = True

    class BMFMeta:
        search_fields = ['name']
        has_logging = True
        has_comments = True
        has_files = True
        serializer = ProjectSerializer


class Project(AbstractProject):
    pass
