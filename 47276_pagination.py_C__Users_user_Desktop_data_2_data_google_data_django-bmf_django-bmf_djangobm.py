#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from djangobmf.pagination import PaginationMixin


class ActivityPagination(PaginationMixin):
    pass


class DocumentPagination(PaginationMixin):
    pass


class RelatedPagination(PaginationMixin):
    pass
