#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.core.paginator import Paginator
from django.core.paginator import InvalidPage
from django.template import Context
from django.template import loader
from django.utils import six
from django.utils.translation import ugettext_lazy as _

from rest_framework.exceptions import NotFound
from rest_framework.pagination import BasePagination
from rest_framework.response import Response
from rest_framework.utils.urls import replace_query_param
from rest_framework.utils.urls import remove_query_param


class PaginationMixin(BasePagination):
    template = 'rest_framework/pagination/previous_and_next.html'
    invalid_page_message = _('Invalid page "{page_number}": {message}.')
    page_size = None

    def paginate_queryset(self, queryset, request, view=None):
        self.request = request

        if not self.page_size:
            self.page = None
            self.count = queryset.count()
            return list(queryset)

        paginator = Paginator(queryset, self.page_size)
        page_number = request.query_params.get('page', 1)
        self.count = paginator.count

        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            msg = self.invalid_page_message.format(
                page_number=page_number,
                message=six.text_type(exc),
            )
            raise NotFound(msg)

        if paginator.num_pages > 1:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        return list(self.page)

    def get_paginated_response_data(self, data):
        if self.page:
            return {
                'paginator': {
                    'current': self.page.number,
                    'count': self.count,
                    'pages': self.page.paginator.num_pages,
                },
                'items': data,
            }
        else:
            return {
                'paginator': {
                    'current': 1,
                    'count': self.count,
                    'pages': 1,
                },
                'items': data,
            }

    def get_paginated_response(self, data):
        return Response(self.get_paginated_response_data(data))

    def get_next_link(self):
        if not self.page or not self.page.has_next():
            return None
        url = self.request.build_absolute_uri()
        page_number = self.page.next_page_number()
        return replace_query_param(url, 'page', page_number)

    def get_previous_link(self):
        if not self.page or not self.page.has_previous():
            return None
        url = self.request.build_absolute_uri()
        page_number = self.page.previous_page_number()
        if page_number == 1:
            return remove_query_param(url, 'page')
        return replace_query_param(url, 'page', page_number)

    def get_html_context(self):
        return {
            'previous_url': self.get_previous_link(),
            'next_url': self.get_next_link(),
        }

    def to_html(self):
        template = loader.get_template(self.template)
        context = Context(self.get_html_context())
        return template.render(context)


class ModulePagination(PaginationMixin):
    page_size = 100
