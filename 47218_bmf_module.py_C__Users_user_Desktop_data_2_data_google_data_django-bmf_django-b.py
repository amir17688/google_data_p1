#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _

from djangobmf.sites import Module
from djangobmf.sites import ViewMixin
from djangobmf.sites import register
from djangobmf.sites import site

from .categories import ProductCategory
from .models import Product
from .models import ProductTax
from .models import PRODUCT_SERVICE
from .views import ProductDetailView
from .views import ProductCreateView
from .views import ProductUpdateView


@register
class ProductModule(Module):
    model = Product
    default = True
    create = ProductCreateView
    update = ProductUpdateView
    detail = ProductDetailView


@register
class ProductTaxModule(Module):
    model = ProductTax
    default = True


site.register_settings('bmfcontrib_product', {
    'default': forms.ModelChoiceField(queryset=Product.objects.filter(type=PRODUCT_SERVICE)),
})


@register(category=ProductCategory)
class SellableProducts(ViewMixin):
    model = Product
    name = _("Sellable products")
    slug = "sell"

    def filter_queryset(self, request, queryset, view):
        return queryset.filter(
            can_sold=True,
        )


@register(category=ProductCategory)
class PurchaseableProducts(ViewMixin):
    model = Product
    name = _("Purchaseable products")
    slug = "purchase"

    def filter_queryset(self, request, queryset, view):
        return queryset.filter(
            can_purchased=True,
        )


@register(category=ProductCategory)
class AllProducts(ViewMixin):
    model = Product
    name = _("All products")
    slug = "all"
