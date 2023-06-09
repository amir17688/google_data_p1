import logging
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import Http404
import collections
import itertools
from django import forms
from django.utils.translation import ugettext as _
from corehq.apps.app_manager.analytics import get_exports_by_application
from corehq.apps.app_manager.dbaccessors import get_apps_in_domain, get_app
from corehq.apps.app_manager.models import Application
from corehq.form_processor.interfaces.dbaccessors import CaseAccessors
from couchforms.analytics import get_exports_by_form
from couchforms.models import XFormInstance
from dimagi.utils.decorators.memoized import memoized


ApplicationDataSource = collections.namedtuple('ApplicationDataSource', ['application', 'source_type', 'source'])
RMIDataChoice = collections.namedtuple('RMIDataChoice', ['id', 'text', 'data'])
AppFormRMIResponse = collections.namedtuple('AppFormRMIResponse', [
    'app_types', 'apps_by_type', 'modules_by_app',
    'forms_by_app_by_module', 'placeholders'
])
AppFormRMIPlaceholder = collections.namedtuple('AppFormRMIPlaceholder', [
    'application', 'module', 'form'
])
AppCaseRMIResponse = collections.namedtuple('AppCaseRMIResponse', [
    'app_types', 'apps_by_type', 'case_types_by_app', 'placeholders'
])
AppCaseRMIPlaceholder = collections.namedtuple('AppCaseRMIPlaceholder', [
    'application', 'case_type'
])


class ApplicationDataSourceUIHelper(object):
    """
    A helper object that can be used in forms that allows you to select a data source from an application.
    Data sources can be forms and cases.

    To use it you must do the following:

    - Add this helper as a member variable of your form
    - Call helper.boostrap() with the domain.
    - Add helper.get_fields() to the form fields.
    - Add the following knockout bindings to your template:

        $(function () {
            $("#FORM").koApplyBindings({
                application: ko.observable(""),
                sourceType: ko.observable(""),
                sourcesMap: {{ sources_map|JSON }}
            });
        });

    Where FORM is a selector for your form and sources_map is the .all_sources property from this object
    (which gets set after bootstrap).

    See usages for examples.
    """

    def __init__(self, enable_cases=True, enable_forms=True):
        self.all_sources = {}
        self.enable_cases = enable_cases
        self.enable_forms = enable_forms
        source_choices = []
        if enable_cases:
            source_choices.append(("case", _("Case")))
        if enable_forms:
            source_choices.append(("form", _("Form")))

        self.application_field = forms.ChoiceField(label=_('Application'), widget=forms.Select())
        if enable_cases and enable_forms:
            self.source_type_field = forms.ChoiceField(label=_('Type of Data'),
                                                       choices=source_choices,
                                                       widget=forms.Select(choices=source_choices))
        else:
            self.source_type_field = forms.ChoiceField(choices=source_choices,
                                                       widget=forms.HiddenInput(),
                                                       initial=source_choices[0][0])

        self.source_field = forms.ChoiceField(label=_('Data Source'), widget=forms.Select())

    def bootstrap(self, domain):
        self.all_sources = get_app_sources(domain)
        self.application_field.choices = sorted(
            [(app_id, source['name']) for app_id, source in self.all_sources.items()],
            key=lambda id_name_tuple: (id_name_tuple[1] or '').lower()
        )
        self.source_field.choices = []

        def _add_choices(field, choices):
            field.choices.extend(choices)
            # it's weird/annoying that you have to manually sync these
            field.widget.choices.extend(choices)

        if self.enable_cases:
            _add_choices(
                self.source_field,
                [(ct['value'], ct['text']) for app in self.all_sources.values() for ct in app['case']]
            )
        if self.enable_forms:
            _add_choices(
                self.source_field,
                [(ct['value'], ct['text']) for app in self.all_sources.values() for ct in app['form']]
            )

        # NOTE: This corresponds to a view-model that must be initialized in your template.
        # See the doc string of this class for more information.
        self.application_field.widget.attrs = {'data-bind': 'value: application'}
        self.source_type_field.widget.attrs = {'data-bind': 'value: sourceType'}
        self.source_field.widget.attrs = {'data-bind': '''
            options: sourcesMap[application()][sourceType()],
            optionsText: function(item){return item.text},
            optionsValue: function(item){return item.value}
        '''}

    def get_fields(self):
        fields = collections.OrderedDict()
        fields['source_type'] = self.source_type_field
        fields['application'] = self.application_field
        fields['source'] = self.source_field
        return fields

    def get_app_source(self, data_dict):
        return ApplicationDataSource(data_dict['application'], data_dict['source_type'], data_dict['source'])


def get_app_sources(domain):
    apps = get_apps_in_domain(domain, include_remote=False)
    return {
        app._id: {
            "name": app.name,
            "case": [{"text": t, "value": t} for t in app.get_case_types()],
            "form": [
                {
                    "text": u'{} / {}'.format(form.get_module().default_name(), form.default_name()),
                    "value": form.get_unique_id()
                } for form in app.get_forms()
            ]
        }
        for app in apps
    }


class ApplicationDataRMIHelper(object):
    """ApplicationDataRMIHelper is meant to generate the response for the
    djangoRMI methods required to initialize form controlled by
    hq.app_data_drilldown.ng.js.

    Note / todo: This Helper should be merged with ApplicationDataSourceUIHelper.
    Holding off to a different PR, as I want to isolate QA to just the exports
    (the first thing to use this) --Biyeun

    """
    UNKNOWN_SOURCE = '_unknown'

    APP_TYPE_ALL = 'all'
    APP_TYPE_DELETED = 'deleted'
    APP_TYPE_REMOTE = 'remote'
    APP_TYPE_NONE = 'no_app'
    APP_TYPE_UNKNOWN = 'unknown'

    def __init__(self, domain, as_dict=True, form_placeholders=None, case_placeholders=None):
        self.domain = domain
        self.as_dict = as_dict
        default_form_placeholder = AppFormRMIPlaceholder(
            application=_("Select Application"),
            module=_("Select Module"),
            form=_("Select Form"),
        )
        self.form_placeholders = form_placeholders or default_form_placeholder
        default_case_placeholder = AppCaseRMIPlaceholder(
            application=_("Select Application"),
            case_type=_("Select Case Type"),
        )
        self.case_placeholders = case_placeholders or default_case_placeholder
        if self.as_dict:
            self.form_placeholders = self.form_placeholders._asdict()
            self.case_placeholders = self.case_placeholders._asdict()

    def _get_unknown_form_possibilities(self):
        possibilities = collections.defaultdict(list)
        for app in get_exports_by_application(self.domain):
            # index by xmlns
            x = app['value']
            x['has_app'] = True
            possibilities[app['key'][2]].append(x)
        return possibilities

    def _attach_unknown_suggestions(self, unknown_forms):
        """If there are any unknown forms, try and find the best possible matches
        from deleted apps or copied apps. If no suggestion is found, say so
        but provide the xmlns.
        """
        if unknown_forms:
            possibilities = self._get_unknown_form_possibilities()

            class AppCache(dict):
                def __init__(self, domain):
                    super(AppCache, self).__init__()
                    self.domain = domain

                def __getitem__(self, item):
                    if item not in self:
                        try:
                            self[item] = get_app(app_id=item, domain=self.domain)
                        except Http404:
                            pass
                    return super(AppCache, self).__getitem__(item)

            app_cache = AppCache(self.domain)

            for form in unknown_forms:
                app = None
                if form['app']['id']:
                    try:
                        app = app_cache[form['app']['id']]
                        form['has_app'] = True
                    except KeyError:
                        form['app_does_not_exist'] = True
                        form['possibilities'] = possibilities[form['xmlns']]
                        if form['possibilities']:
                            form['duplicate'] = True
                    else:
                        if app.domain != self.domain:
                            logging.error("submission tagged with app from wrong domain: %s" % app.get_id)
                        else:
                            if app.copy_of:
                                try:
                                    app = app_cache[app.copy_of]
                                    form['app_copy'] = {'id': app.get_id, 'name': app.name}
                                except KeyError:
                                    form['app_copy'] = {'id': app.copy_of, 'name': '?'}
                            if app.is_deleted():
                                form['app_deleted'] = {'id': app.get_id}
                            try:
                                app_forms = app.get_xmlns_map()[form['xmlns']]
                            except AttributeError:
                                # it's a remote app
                                app_forms = None
                                form['has_app'] = True
                            if app_forms:
                                app_form = app_forms[0]
                                if app_form.doc_type == 'UserRegistrationForm':
                                    form['is_user_registration'] = True
                                else:
                                    app_module = app_form.get_module()
                                    form['module'] = app_module
                                    form['form'] = app_form
                                form['show_xmlns'] = False

                            if not form.get('app_copy') and not form.get('app_deleted'):
                                form['no_suggestions'] = True
                    if app:
                        form['app'] = {'id': app.get_id, 'name': app.name, 'langs': app.langs}
                else:
                    form['possibilities'] = possibilities[form['xmlns']]
                    if form['possibilities']:
                        form['duplicate'] = True
                    else:
                        form['no_suggestions'] = True
        return unknown_forms

    @staticmethod
    def _sorkey_form(form):
        app_id = form['app']['id']
        if form.get('has_app', False):
            order = 0 if not form.get('app_deleted') else 1
            app_name = form['app']['name']
            module = form.get('module')
            if module:
                # module is sometimes wrapped json, sometimes a dict!
                module_id = module['id'] if 'id' in module else module.id
            else:
                module_id = -1 if form.get('is_user_registration') else 1000
            app_form = form.get('form')
            if app_form:
                # app_form is sometimes wrapped json, sometimes a dict!
                form_id = app_form['id'] if 'id' in app_form else app_form.id
            else:
                form_id = -1
            return (order, app_name, app_id, module_id, form_id)
        else:
            form_xmlns = form['xmlns']
            return (2, form_xmlns, app_id)

    @property
    @memoized
    def _all_forms(self):
        forms = []
        unknown_forms = []
        for f in get_exports_by_form(self.domain):
            form = f['value']
            if form.get('app_deleted') and not form.get('submissions'):
                continue
            if 'app' in form:
                form['has_app'] = True
                forms.append(form)
            else:
                app_id = f['key'][1] or ''
                form['app'] = {
                    'id': app_id
                }
                form['has_app'] = False
                form['show_xmlns'] = True
                unknown_forms.append(form)
        forms.extend(self._attach_unknown_suggestions(unknown_forms))
        return sorted(forms, key=self._sorkey_form)

    @property
    @memoized
    def _no_app_forms(self):
        return filter(lambda f: not f.get('has_app', False), self._all_forms)

    @property
    @memoized
    def _remote_app_forms(self):
        return filter(lambda f: f.get('has_app', False) and f.get('show_xmlns', False), self._all_forms)

    @property
    @memoized
    def _deleted_app_forms(self):
        return filter(
            lambda f: f.get('has_app', False) and f.get('app_deleted') and not f.get('show_xmlns', False),
            self._all_forms
        )

    @property
    @memoized
    def _available_app_forms(self):
        return filter(
            lambda f: f.get('has_app', False) and not f.get('app_deleted') and not f.get('show_xmlns', False),
            self._all_forms
        )

    @property
    @memoized
    def _unknown_forms(self):
        return itertools.chain(self._deleted_app_forms, self._remote_app_forms, self._no_app_forms)

    def _get_app_type_choices(self, as_dict=True):
        choices = [(_("Applications"), self.APP_TYPE_ALL)]
        if self._remote_app_forms or self._deleted_app_forms:
            choices.append((_("Unknown"), self.APP_TYPE_UNKNOWN))
        choices = map(lambda c: RMIDataChoice(id=c[1], text=c[0], data={}), choices)
        if as_dict:
            choices = map(lambda c: c._asdict(), choices)
        return choices

    @staticmethod
    def _get_unique_choices(choices):
        final_choices = collections.defaultdict(list)
        for k, val_list in choices.items():
            new_val_ids = []
            final_choices[k] = []
            for v in val_list:
                if v.id not in new_val_ids:
                    new_val_ids.append(v.id)
                    final_choices[k].append(v)
        return final_choices

    def _get_applications_by_type(self, as_dict=True):
        apps_by_type = (
            (self.APP_TYPE_ALL, self._available_app_forms),
            (self.APP_TYPE_UNKNOWN, self._unknown_forms)
        )
        _app_fmt = lambda c: (c[0], map(lambda f: RMIDataChoice(
            f['app']['id'] if f.get('has_app', False) else self.UNKNOWN_SOURCE,
            f['app']['name'] if f.get('has_app', False) else _("Unknown Application"),
            f
        ), c[1]))
        apps_by_type = map(_app_fmt, apps_by_type)
        apps_by_type = dict(apps_by_type)
        apps_by_type = self._get_unique_choices(apps_by_type)

        # include restore URL for deleted apps
        for app in apps_by_type[self.APP_TYPE_DELETED]:
            app.data['restoreUrl'] = reverse('view_app', args=[self.domain, app.id])

        if as_dict:
            apps_by_type = self._map_chosen_by_choice_as_dict(apps_by_type)
        return apps_by_type

    @staticmethod
    def _map_chosen_by_choice_as_dict(chosen_by_choice):
        for k, v in chosen_by_choice.items():
            chosen_by_choice[k] = map(lambda f: f._asdict(), v)
        return chosen_by_choice

    @staticmethod
    def _get_item_name(item, has_app, app_lang, default_name):
        item_name = None
        if has_app and item is not None:
            item_name = item['name'].get(app_lang) or item['name'].get('en')
        return item_name or default_name

    def _get_modules_and_forms(self, as_dict=True):
        modules_by_app = collections.defaultdict(list)
        forms_by_app_by_module = {}
        for form in self._all_forms:
            has_app = form.get('has_app', False)
            app_lang = form['app']['langs'][0] if 'langs' in form['app'] else 'en'
            app_id = form['app']['id'] if has_app else self.UNKNOWN_SOURCE
            module = form.get('module')
            module_id = (module['id'] if has_app and module is not None
                         else self.UNKNOWN_SOURCE)
            module_name = self._get_item_name(
                module, has_app, app_lang, _("Unknown Module")
            )
            form_xmlns = form['xmlns']
            form_name = form_xmlns
            if not form.get('show_xmlns', False):
                form_name = self._get_item_name(
                    form.get('form'), has_app, app_lang,
                    "{} (potential matches)".format(form_xmlns)
                )
            module_choice = RMIDataChoice(
                module_id,
                module_name,
                form
            )
            form_choice = RMIDataChoice(
                form_xmlns,
                form_name,
                form
            )
            if as_dict:
                form_choice = form_choice._asdict()

            if app_id not in forms_by_app_by_module:
                forms_by_app_by_module[app_id] = collections.defaultdict(list)
            modules_by_app[app_id].append(module_choice)
            forms_by_app_by_module[app_id][module_id].append(form_choice)

        modules_by_app = self._get_unique_choices(modules_by_app)
        if as_dict:
            modules_by_app = self._map_chosen_by_choice_as_dict(modules_by_app)
        return modules_by_app, forms_by_app_by_module

    def get_form_rmi_response(self):
        """Use this to generate the response that initializes the form
        controlled by hq.app_data_drilldown.ng.js if you are drilling down
        to an XForm + app_id pair"""
        modules_by_app, forms_by_app_by_module = self._get_modules_and_forms(self.as_dict)
        response = AppFormRMIResponse(
            app_types=self._get_app_type_choices(self.as_dict),
            apps_by_type=self._get_applications_by_type(self.as_dict),
            modules_by_app=modules_by_app,
            forms_by_app_by_module=forms_by_app_by_module,
            placeholders=self.form_placeholders,
        )
        if self.as_dict:
            response = response._asdict()
        return response

    def _get_cases_for_apps(self, apps_by_type, as_dict=True):
        used_case_types = set()
        case_types_by_app = collections.defaultdict(list)
        for app_type, apps in apps_by_type.items():
            for app_choice in apps:
                if not app_choice.id == self.UNKNOWN_SOURCE:
                    app = get_app(self.domain, app_choice.id)
                    case_types = []
                    if hasattr(app, 'modules'):
                        case_types = set([
                            module.case_type
                            for module in app.modules if module.case_type
                        ])
                        used_case_types = used_case_types.union(case_types)
                        case_types = map(lambda c: RMIDataChoice(
                            id=c,
                            text=c,
                            data=app_choice.data
                        ), case_types)
                        if as_dict:
                            case_types = map(lambda c: c._asdict(), case_types)
                    case_types_by_app[app_choice.id] = case_types
                else:
                    all_case_types = CaseAccessors(self.domain).get_case_types()
                    unknown_case_types = all_case_types.difference(used_case_types)
                    unknown_case_types = map(lambda c: RMIDataChoice(
                        id=c,
                        text=c,
                        data={
                            'unknown': True,
                        }
                    ), unknown_case_types)
                    if as_dict:
                        unknown_case_types = map(lambda c: c._asdict(), unknown_case_types)
                    case_types_by_app[self.UNKNOWN_SOURCE] = unknown_case_types

        return case_types_by_app

    def get_case_rmi_response(self):
        """Use this to generate a response that initializes the form
        controlled by hq.app_data_drilldown.ng.js if you are drilling down to
        a Case Type.
        """
        apps_by_type = self._get_applications_by_type(as_dict=False)
        case_types_by_app = self._get_cases_for_apps(apps_by_type, self.as_dict)
        if self.as_dict:
            apps_by_type = self._map_chosen_by_choice_as_dict(apps_by_type)
        response = AppCaseRMIResponse(
            app_types=self._get_app_type_choices(),
            apps_by_type=apps_by_type,
            case_types_by_app=case_types_by_app,
            placeholders=self.case_placeholders
        )
        if self.as_dict:
            response = response._asdict()
        return response
