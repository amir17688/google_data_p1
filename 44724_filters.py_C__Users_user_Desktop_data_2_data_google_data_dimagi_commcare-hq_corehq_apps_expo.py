from corehq.apps.es import filters as esfilters
from corehq.apps.es.cases import (
    owner,
    is_closed,
    opened_range,
    modified_range,
    user,
    closed_range,
    opened_by,
    owner_type)
from corehq.apps.es.forms import app, submitted, user_id, user_type
from corehq.apps.export.esaccessors import get_group_user_ids
from corehq.pillows.utils import USER_TYPES


def _assert_user_types(user_types):
        if isinstance(user_types, basestring):
            user_types = [user_types]

        for type_ in user_types:
            assert type_ in USER_TYPES, "Expected user type to be in {}, got {}".format(USER_TYPES, type_)


class ExportFilter(object):
    """
    Abstract base class for an export filter on a single case or form property
    """

    def to_es_filter(self):
        """
        Return an ES filter representing this filter
        """
        raise NotImplementedError


class OR(ExportFilter):

    def __init__(self, *args):
        self.operand_filters = args

    def to_es_filter(self):
        return esfilters.OR(*[f.to_es_filter() for f in self.operand_filters])


class AppFilter(ExportFilter):
    """
    Filter on app_id
    """
    def __init__(self, app_id):
        self.app_id = app_id

    def to_es_filter(self):
        return app(self.app_id)


class RangeExportFilter(ExportFilter):

    def __init__(self, gt=None, gte=None, lt=None, lte=None):
        self.gt = gt
        self.gte = gte
        self.lt = lt
        self.lte = lte


class OwnerFilter(ExportFilter):
    """
    Filter on owner_id
    """
    def __init__(self, owner_id):
        self.owner_id = owner_id

    def to_es_filter(self):
        return owner(self.owner_id)


class OwnerTypeFilter(ExportFilter):
    def __init__(self, owner_type):
        _assert_user_types(owner_type)
        self.owner_types = owner_type

    def to_es_filter(self):
        return owner_type(self.owner_types)


class IsClosedFilter(ExportFilter):
    """
    Filter on case closed property
    """
    def __init__(self, is_closed):
        self.is_closed = is_closed

    def to_es_filter(self):
        return is_closed(self.is_closed)


class NameFilter(ExportFilter):

    def __init__(self, case_name):
        self.case_name = case_name

    def to_es_filter(self):
        return esfilters.term('name', self.case_name)


class OpenedOnRangeFilter(RangeExportFilter):

    def to_es_filter(self):
        return opened_range(self.gt, self.gte, self.lt, self.lte)


class OpenedByFilter(ExportFilter):

    def __init__(self, opened_by):
        self.opened_by = opened_by

    def to_es_filter(self):
        return opened_by(self.opened_by)


class ModifiedOnRangeFilter(RangeExportFilter):

    def to_es_filter(self):
        return modified_range(self.gt, self.gte, self.lt, self.lte)


class LastModifiedByFilter(ExportFilter):

    def __init__(self, last_modified_by):
        self.last_modified_by = last_modified_by

    def to_es_filter(self):
        return user(self.last_modified_by)


class ClosedOnRangeFilter(RangeExportFilter):

    def to_es_filter(self):
        return closed_range(self.gt, self.gte, self.lt, self.lte)


class ClosedByFilter(ExportFilter):

    def __init__(self, closed_by):
        self.closed_by = closed_by

    def to_es_filter(self):
        return esfilters.term("closed_by", self.closed_by)


class GroupFilter(ExportFilter):  # Abstract base class
    base_filter = None

    def __init__(self, group_id):
        self.group_id = group_id

    def to_es_filter(self):
        user_ids = get_group_user_ids(self.group_id)
        return self.base_filter(user_ids).to_es_filter()


class GroupOwnerFilter(GroupFilter):
    base_filter = OwnerFilter


class GroupLastModifiedByFilter(GroupFilter):
    base_filter = LastModifiedByFilter


class GroupClosedByFilter(GroupFilter):
    base_filter = ClosedByFilter


class ReceivedOnRangeFilter(RangeExportFilter):
    def to_es_filter(self):
        return submitted(self.gt, self.gte, self.lt, self.lte)


class FormSubmittedByFilter(ExportFilter):
    def __init__(self, submitted_by):
        self.submitted_by = submitted_by

    def to_es_filter(self):
        return user_id(self.submitted_by)


class UserTypeFilter(ExportFilter):
    def __init__(self, user_types):
        _assert_user_types(user_types)
        self.user_types = user_types

    def to_es_filter(self):
        return user_type(self.user_types)


class GroupFormSubmittedByFilter(GroupFilter):
    base_filter = FormSubmittedByFilter
