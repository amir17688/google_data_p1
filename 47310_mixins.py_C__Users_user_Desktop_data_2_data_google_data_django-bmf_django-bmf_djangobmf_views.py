#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse_lazy
from django.db.models.query import QuerySet
from django.forms.models import modelform_factory
from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from djangobmf import get_version
from djangobmf.conf import settings as bmfsettings
from djangobmf.core.employee import Employee
from djangobmf.decorators import login_required
from djangobmf.permissions import AjaxPermission
from djangobmf.utils.serializers import DjangoBMFEncoder
from djangobmf.views.defaults import bad_request
from djangobmf.views.defaults import permission_denied
from djangobmf.views.defaults import page_not_found
from djangobmf.views.defaults import server_error

import json
import re
try:
    from urllib import parse
except ImportError:
    import urlparse as parse

import logging
logger = logging.getLogger(__name__)


class BaseMixin(object):
    """
    provides functionality used in EVERY view throughout the application.
    this provides us with more flexibility and removes the need to define
    a middleware.
    """
    # use permission classes to overwrite the permissions for a specific view
    permission_classes = []

    # default permission classes
    default_permission_classes = []

    # Function name and parameters are identical to the django rest framework
    def check_permissions(self, request):
        """
        checks all the permissions given in permission_classes and default_permission_classes
        """
        for permission in self.default_permission_classes:
            if not permission().has_permission(request, self):
                return False
        for permission in self.permission_classes:
            if not permission().has_permission(request, self):
                return False
        return True

    # Function name and parameters are identical to the django rest framework
    def check_object_permissions(self, request, obj):
        """
        checks all the permissions given in permission_classes
        """

        for permission in self.default_permission_classes:
            if not permission().has_object_permission(request, self, obj):
                return False

        for permission in self.permission_classes:
            if not permission().has_object_permission(request, self, obj):
                return False

        return True

    def get_bmfcontenttype(self):
        return ContentType.objects.get_for_model(self.get_bmfmodel())

    def get_bmfmodel(self):
        """
        return the model property or loads the model dynamically
        via the url kwargs (app, model) or throws a LookupError
        """
        if getattr(self, 'model', None):
            return self.model

        if 'app' not in self.kwargs or 'model' not in self.kwargs:
            raise LookupError()

        # Raises also a LookupError, when it does not find a model
        self.model = apps.get_model(self.kwargs.get('app'), self.kwargs.get('model'))
        return self.model

    def get_bmfqueryset(self, filter=True):
        if filter:
            return self.get_bmfmodel()._bmfmeta.filter_queryset(
                self.get_bmfqueryset(filter=False),
                self.request.user,
            )
        return self.get_bmfmodel().objects.all()

    def get_bmfobject(self, pk):
        try:
            return self.get_bmfqueryset().get(pk=pk)
        except self.get_bmfmodel().DoesNotExist:
            if self.get_bmfqueryset(filter=False).filter(pk=pk).count():
                raise PermissionDenied
            raise Http404

    def _read_session_data(self):
        """
        returns the data saved in the session or an
        default dictionary containing the version of
        the bmf
        """
        return self.request.session.get("djangobmf", {
            'version': get_version(),
            'debugjs': bmfsettings.DEBUG_JS,
        })

    def _write_session_data(self, data):
        """
        stores the session under the request object
        and marks the session as modified, so django will
        save it
        """
        # reload sessiondata, because we can not be sure, that the
        # session was not changed during this request
        session_data = self._read_session_data()
        session_data.update(data)

        # update session
        self.request.session["djangobmf"] = session_data
        self.request.session.modified = True

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        """
        checks permissions, requires a login and
        because we are using a generic view approach to the data-models
        in django BMF, we can ditch a middleware (less configuration)
        and add the functionality we need for the framework to
        work properly to this function.
        """

        # add the site object to every request
        setattr(self.request, 'djangobmf_appconfig', apps.get_app_config(bmfsettings.APP_LABEL))
        setattr(self.request, 'djangobmf_site', self.request.djangobmf_appconfig.site)

        # add the authenticated user and employee to the request (as a lazy queryset)
        self.request.user.djangobmf = Employee(self.request.user)

        # TODO ... call check_object_permission instead when objects have a model
        try:
            if not self.check_permissions(self.request):
                return permission_denied(self.request)
        except Http404:
            return page_not_found(self.request)

        # TODO MOVE THIS CHECK TO PERMISSIONS
        # check if bmf has a employee model and if so do a validation of the
        # employee instance (users, who are not employees are not allowed to access)
        if self.request.user.djangobmf.has_employee and not self.request.user.djangobmf.employee:
            logger.debug("User %s does not have permission to access djangobmf" % self.request.user)
            if self.request.user.is_superuser:
                return redirect('djangobmf:wizard', permanent=False)
            else:
                return permission_denied(self.request)

        response = super(BaseMixin, self).dispatch(*args, **kwargs)

        # Catch HTTP error codes and redirect to a bmf-specific template
        if response.status_code in [400, 403, 404, 500] and not settings.DEBUG:

            if response.status_code == 400:
                return bad_request(self.request)

            if response.status_code == 403:
                return permission_denied(self.request)

            if response.status_code == 404:
                return page_not_found(self.request)

            if response.status_code == 500:
                return server_error(self.request)

        return response


class BaseAPIMixin(BaseMixin):
    """
    Adds additional functions to `BaseMixin` needed for the REST API
    """
    pass


class BaseViewMixin(BaseMixin):
    """
    Adds additional functions to `BaseMixin` needed for view functions
    """
    def get_context_data(self, **kwargs):
        # update context with session data
        kwargs.update({
            'djangobmf': self._read_session_data(),
        })

        # always read current version, if in DEBUG mode
        if settings.DEBUG:
            kwargs["djangobmf"]['version'] = get_version()

        return super(BaseViewMixin, self).get_context_data(**kwargs)


class ViewMixin(BaseViewMixin):
    pass


class AjaxMixin(BaseMixin):
    """
    add some basic function for ajax requests
    """
    permission_classes = [AjaxPermission]

    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(AjaxMixin, self).dispatch(*args, **kwargs)

    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context, cls=DjangoBMFEncoder)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)

    def get_ajax_context(self, **context):
        return context

    def render_to_response(self, context, **response_kwargs):
        """
        If the view calls a render_to_response, the context is rendered and added
        to the json-response object as a html attribute
        """
        response = super(AjaxMixin, self).render_to_response(context, **response_kwargs)
        response.render()
        ctx = self.get_ajax_context(**{
            'html': response.rendered_content,
        })
        return self.render_to_json_response(ctx)

    def render_valid_form(self, context):
        ctx = {
            'success': True,
        }
        ctx.update(context)
        return self.render_to_json_response(ctx)


class NextMixin(object):
    """
    redirects to an url or to next, if it is set via get
    """

    def redirect_next(self, reverse=None, *args, **kwargs):
        if 'next' in self.request.GET:
            redirect_to = self.request.GET.get('next', '')

            netloc = parse.urlparse(redirect_to)[1]
            if not netloc or netloc == self.request.get_host():
                return redirect_to

        if hasattr(self, 'success_url') and self.success_url:
            return self.success_url

        if reverse:
            return reverse_lazy(reverse, args=args, kwargs=kwargs)

        return self.request.path_info


class ReadOnlyMixin(object):

    def get_initial(self):
        initial = super(ReadOnlyMixin, self).get_initial()
        self.readonly_fields = []

        for key in self.request.GET.keys():
            match = re.match(r'^set-(\w+)$|^data\[(\w+)\]$', key)
            if match:
                field = match.group(1) or match.group(2)
                initial.update({field: self.request.GET.get(key)})
                self.readonly_fields.append(field)

        return initial

    def get_form(self, *args, **kwargs):
        form = super(ReadOnlyMixin, self).get_form(*args, **kwargs)

        for field in self.readonly_fields:
            if field in form.fields:
                form.fields[field].widget.attrs['readonly'] = True
            else:
                raise ImproperlyConfigured(
                    "Form %s in view %s has no field named %s" % (
                        self.form.__class__.__name__,
                        self.__class__.__name__,
                        field
                    )
                )
        return form


# MODULES

class ModuleBaseMixin(object):
    model = None
    module = None

    def get_queryset(self, manager=None):
        """
        Return the list of items for this view.
        `QuerySet` in which case `QuerySet` specific behavior will be enabled.
        """
        module = self.request.djangobmf_site.get_module(self.model)

        if self.model and manager:
            if module.manager.get(manager, None):
                qs = module.manager[manager]
                if isinstance(qs, QuerySet):
                    qs = qs.all()
            elif hasattr(self.model._default_manager, manager):
                qs = getattr(self.model._default_manager, manager)(self.request)
            else:
                raise ImproperlyConfigured(
                    "%(manager)s is not defined in %(cls)s.model" % {
                        'manager': manager,
                        'cls': self.__class__.__name__
                    }
                )

        elif self.model is not None:
            qs = self.model._default_manager.all()
        else:
            raise ImproperlyConfigured(
                "%(cls)s is missing a QuerySet. Define "
                "%(cls)s.model " % {
                    'cls': self.__class__.__name__
                }
            )

        # load employee and team data into user
        self.request.user.djangobmf = Employee(self.request.user)

        return self.module.permissions().filter_queryset(qs, self.request.user)

    def get_object(self):
        if hasattr(self, 'object'):
            return self.object
        return super(ModuleBaseMixin, self).get_object()

    def get_context_data(self, **kwargs):
        info = self.model._meta.app_label, self.model._meta.model_name
        kwargs.update({
            'bmfmodule': {
                'verbose_name_plural': self.model._meta.verbose_name_plural,
                'create_views': self.model._bmfmeta.create_views,
                'report_views': self.model._bmfmeta.report_views,
                'model': self.model,
                # 'contenttype': ContentType.objects.get_for_model(self.model).pk,
                # 'has_report': self.model._bmfmeta.has_report,
                'can_clone': self.model._bmfmeta.can_clone and self.request.user.has_perms([
                    '%s.view_%s' % info,
                    '%s.clone_%s' % info,
                ]),
                # 'verbose_name': self.model._meta.verbose_name,  # unused
            },
        })
        if self.model._bmfmeta.has_workflow and hasattr(self, 'object') and self.object:
            kwargs.update({
                'bmfworkflow': self.object._bmfmeta.workflow,
                'bmfworkflow_transitions': self.object._bmfmeta.workflow.transitions(self.request.user),
            })
        return super(ModuleBaseMixin, self).get_context_data(**kwargs)


class ModuleAjaxMixin(ModuleBaseMixin, AjaxMixin):
    """
    base mixin for update, clone, delete and create views (ajax-forms)
    """

    def get_ajax_context(self, **context):
        ctx = {
            # if an object is created or changed return the object's pk on success
            'object_pk': 0,

            # on success set this to True
            'success': False,

            # reload page on success
            'reload': False,

            # OR redirect on success
            'redirect': None,

            # OR reload messages on success
            'message': False,

            # returned html
            'html': None,

            # return error messages
            'errors': [],
        }
        ctx.update(context)
        return ctx

    def render_valid_form(self, context):
        #   if 'redirect' not in context and not self.model._bmfmeta.only_related:
        #       context.update({
        #           'redirect': self.get_success_url(),
        #       })
        return super(ModuleAjaxMixin, self).render_valid_form(context)


class ModuleViewMixin(ModuleBaseMixin, ViewMixin):
    """
    Basic objects, includes bmf-specific functions and context
    variables for bmf-views
    """
    pass


class ModuleSearchMixin(object):
    """
    Adds the methods ``normalize_query`` and ``construct_search``
    """

    def normalize_query(
            self, query_string, findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
            normspace=re.compile(r'\s{2,}').sub):
        '''
        Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.

        Example:
        > self.normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']

        '''
        return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]

    # Apply keyword searches.
    def construct_search(self, field_name):
        if field_name.startswith('^'):
            return "%s__istartswith" % field_name[1:]
        elif field_name.startswith('='):
            return "%s__iexact" % field_name[1:]
        elif field_name.startswith('@'):
            return "%s__search" % field_name[1:]
        else:
            return "%s__icontains" % field_name


class ModuleFormMixin(object):
    """
    make an BMF-Form
    """
    fields = None
    exclude = []

    def get_form_class(self, *args, **kwargs):
        """
        Returns the form class to use in this view.
        """
        if not self.form_class:
            if self.model is not None:
                # If a model has been explicitly provided, use it
                model = self.model
            elif hasattr(self, 'object') and self.object is not None:
                # If this view is operating on a single object, use
                # the class of that object
                model = self.object.__class__
            else:
                # Try to get a queryset and extract the model class
                # from that
                model = self.get_queryset().model

            if isinstance(self.fields, list):
                self.form_class = modelform_factory(model, fields=self.fields)
            else:
                self.form_class = modelform_factory(model, exclude=self.exclude)
        return self.form_class
