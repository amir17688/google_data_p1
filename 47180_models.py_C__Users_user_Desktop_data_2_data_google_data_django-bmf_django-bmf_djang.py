#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from djangobmf.conf import settings
from djangobmf.models import BMFModel
from djangobmf.fields import CountryField

from .serializers import AddressSerializer


class BaseAddress(BMFModel):
    customer = models.ForeignKey(
        settings.CONTRIB_CUSTOMER, null=False, blank=False,
        related_name="customer_address", on_delete=models.CASCADE,
    )

    is_active = models.BooleanField(_('Is active'), default=True)
    is_billing = models.BooleanField(_('Is billing'), default=True)
    is_shipping = models.BooleanField(_('Is shipping'), default=True)
    default_billing = models.BooleanField(_('Default billing'), default=False)
    default_shipping = models.BooleanField(_('Default shipping'), default=False)

    class Meta:
        verbose_name = _('Address')
        verbose_name_plural = _('Addresses')
        ordering = ['name']
        abstract = True
        swappable = "BMF_CONTRIB_ADDRESS"

    def as_report(self):
        raise NotImplementedError(
            'You need to implement a function to print your address in a report'
        )

    def bmfget_customer(self):
        return self.customer


@python_2_unicode_compatible
class AbstractAddress(BaseAddress):
    """
    """
    name = models.CharField(_('Name'), max_length=255, null=True, blank=False, )
    name2 = models.CharField(_('Name2'), max_length=255, null=True, blank=True, )
    street = models.CharField(_('Street'), max_length=255, null=True, blank=False, )
    zip = models.CharField(_('Zipcode'), max_length=255, null=True, blank=False, )
    city = models.CharField(_('City'), max_length=255, null=True, blank=False, )
    state = models.CharField(_('State'), max_length=255, null=True, blank=True, )
    old_country = models.CharField(
        _('Country OLD'), max_length=255, null=True, blank=True,
        help_text="This field will be removed in an upcoming release of djangobmf"
    )
    country = CountryField(_('Country'))

    class Meta(BaseAddress.Meta):
        abstract = True

    class BMFMeta:
        observed_fields = ['name', 'name2', 'street', 'zip', 'city', 'state', 'country']
        serializer = AddressSerializer

    def as_report(self):
        return _(
            "%(name)s %(name2)s\n%(street)s\n%(city)s, %(state)s, %(zip)s, %(country)s" % {
                'name': self.name,
                'name2': "\n" + self.name2,
                'street': self.street,
                'zip': self.zip,
                'city': self.city,
                'state': self.state,
                'country': self.country.alpha2,
            }
        )

    def __str__(self):
        name = self.name
        if self.name2:
            name += ", " + self.name2
        return '%s, %s, %s (%s)' % (
            name,
            self.street,
            self.city,
            self.country.alpha2,
        )


class Address(AbstractAddress):
    pass
