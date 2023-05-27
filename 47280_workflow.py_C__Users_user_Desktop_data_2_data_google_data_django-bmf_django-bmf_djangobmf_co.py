#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django.core.exceptions import ValidationError
from django.utils import six
from django.utils.encoding import force_text
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from rest_framework.reverse import reverse

from djangobmf.core.employee import Employee
from djangobmf.signals import activity_workflow

import inspect
from collections import OrderedDict


@python_2_unicode_compatible
class State(object):
    """

    Args:
        * name: Verbose name of the State
        * default: True if this is the default state
        * update: Update-View is available, when in this state (default: True)
        * delete: Delete-View is available, when in this state (default: True)
    """
    _creation_counter = 0

    def __init__(self, name, default=False, update=True, delete=True):
        self.name = name
        self.default = default
        self.update = update
        self.delete = delete

        self._order = State._creation_counter
        State._creation_counter += 1

    def __str__(self):
        return force_text(self.name)

    def __repr__(self):
        return force_text("<%s: '%s'>" % (self.__class__.__name__, str(self)))


@python_2_unicode_compatible
class Transition(object):
    """
    Args:
        * name: Verbose name of the Transition
        * sources: From state
        * target: To state(s) - can be either a list of state keys or a single state key
        * validate: Validate the model when changeing the state (default: True)
        * permissions: List of django permissions to check
        * condition: a function which is used to check user related conditions
    """
    _creation_counter = 0

    def __init__(self, name, sources, target, validate=True, permissions=[], condition=None):
        self.name = name

        if isinstance(sources, six.string_types):
            self.sources = [sources]
        elif hasattr(sources, '__iter__'):
            self.sources = list(sources)
        else:
            # LOOK: you may even add a non-interable object to this dont know why it may be used
            #       maybe it'll be better to raise an acception and accept only
            #       string objects (and even check the iterable object if it returns strings)
            self.sources = [sources]
        self.target = target

        # use object validation bevor object is changed
        self.validate = validate

        # list with permissions
        self.permissions = permissions

        # define a condition for this transition
        self.condition = condition

        if permissions or condition:
            self.conditioned = True
        else:
            self.conditioned = False

        self._order = Transition._creation_counter
        Transition._creation_counter += 1

    def __str__(self):
        return force_text(self.name)

    def __repr__(self):
        return force_text("<%s: '%s'>" % (self.__class__.__name__, str(self)))

    def affected_states(self):
        return self.sources + [self.target]

    def eval_condition(self, object, user):
        if self.condition:
            return user.has_perms(self.permissions) and self.condition(object, user)
        else:
            return user.has_perms(self.permissions)


class WorkflowMetaclass(type):
    def __new__(cls, name, bases, attrs):
        super_new = super(WorkflowMetaclass, cls).__new__
        parents = [
            b for b in bases if isinstance(b, WorkflowMetaclass) and
            not (b.__name__ == 'NewBase' and b.__mro__ == (b, object))
        ]
        if not parents:
            return super_new(cls, name, bases, attrs)

        # Create the class.
        new_cls = super_new(cls, name, bases, attrs)

        # validation
        if not hasattr(new_cls, 'States'):
            raise ImproperlyConfigured('No states defined in %s' % new_cls)
        if not hasattr(new_cls, 'Transitions'):
            raise ImproperlyConfigured('No transitions defined in %s' % new_cls)

        # set and check states
        new_cls._states = OrderedDict()
        for key, value in sorted(
                inspect.getmembers(
                    new_cls.States,
                    lambda o: isinstance(o, State)
                ), key=lambda i: i[1]._order):
            new_cls._states[key] = value
            if value.default:
                if hasattr(new_cls, '_default_state'):
                    raise ImproperlyConfigured('Two states are defined with an default value in %s' % new_cls)
                else:
                    new_cls._default_state = value
                    new_cls._default_state_key = key
        if len(new_cls._states) == 0:
            raise ImproperlyConfigured('No states defined in %s' % new_cls)
        if not hasattr(new_cls, '_default_state'):
            raise ImproperlyConfigured('You must define a default state in %s' % new_cls)

        # set and check transitions
        new_cls._transitions = OrderedDict()
        for key, value in sorted(
                inspect.getmembers(
                    new_cls.Transitions,
                    lambda o: isinstance(o, Transition)
                ), key=lambda i: i[1]._order):
            if key == "user":
                raise ImproperlyConfigured(
                    'The name "user" is reserved, please rename your transition defined in %s' % new_cls
                )
            if key == "instance":
                raise ImproperlyConfigured(
                    'The name "instance" is reserved, please rename your transition defined in %s' % new_cls
                )
            if key[0] == "_":
                raise ImproperlyConfigured('The keys can not start with an underscore in %s' % new_cls)
            for state in value.affected_states():
                if state not in new_cls._states:
                    raise ImproperlyConfigured('The state %s is not defined in %s' % (state, new_cls))
            new_cls._transitions[key] = value

        # autoset transition functions
        for key, value in new_cls._transitions.items():
            if hasattr(new_cls, key):
                continue

            # function template
            def f(self):
                """
                I'm a template-function. Please overwrite me and let me return either None or a (redirect) URL
                """
                pass
            setattr(new_cls, key, f)

        # return class
        return new_cls


@python_2_unicode_compatible
class Workflow(six.with_metaclass(WorkflowMetaclass, object)):
    """
    Example:

    .. code-block:: python

        class ExampleWorkflow(Workflow):
            class States:
                start = State(_('Start'), default=True, delete=False)
                deleted = State(_('Deleted'), update=False, delete=True)
                accepted = State(_('Accepted'), update=False, delete=True)

            class Transitions:
                accept = State(_('Accept'), 'start', 'accepted')
                delete = State(_('Delete'), ['start', 'accepted'], 'deleted', validate=False)
    """

    def __init__(self, state=None):
        self.instance = None

        if state:
            self._set_state(state)
        else:
            self._current_state = self._default_state
            self._current_state_key = self._default_state_key
        self._initial_state = self._current_state
        self._initial_state_key = self._current_state_key

    def __str__(self):
        return force_text(self._current_state)

    def _from_here(self, object=None, user=None):
        out = []
        for key, transition in self._transitions.items():
            if self._current_state_key in transition.sources:
                if object and user and not transition.eval_condition(object, user):
                    continue
                out.append((key, transition))
        return out

    def _set_state(self, key):
        if key not in self._states:
            raise ValidationError(_("The state %s is not valid") % key)
        self._current_state = self._states[key]
        self._current_state_key = key

    def _call(self, key, instance, user):

        # check if key is valid
        if self._current_state_key not in self._transitions[key].sources:
            raise ValidationError(_("This transition is not valid"))

        user.djangobmf = Employee(user)

        # update object with instance and user (they come in handy in user-defined functions)
        self.instance = instance
        self.user = user

        # normaly the instance attribute should only be unset during the tests
        if not self.instance:
            self._set_state(self._transitions[key].target)
            return getattr(self, key)()

        # validate the instance
        if self._transitions[key].validate and self._current_state.update:
            self.instance.full_clean()

        # check the conditions of the transition
        if self._transitions[key].conditioned:
            self._transitions[key].eval_condition(instance, user)

        # everything is valid, we can set the new state
        self._set_state(self._transitions[key].target)

        # call function
        url = getattr(self, key)()

        return url


@python_2_unicode_compatible
class WorkflowContainer(object):
    """
    This object is generated by the workflow-field and saved as it's value
    """

    def __init__(self, workspace, state=None):
        self.obj = workspace(state)
        self.model = None

    def set_django_object(self, obj):
        """
        internal function, which sets the instances object
        called by an post_init signal in djangobmf.models.base
        """
        self.django_object = obj

    @property
    def object(self):
        """
        Returns the current state object
        """
        return self.obj._current_state

    @property
    def name(self):
        """
        Returns the current states name
        """
        return self.obj._current_state.name

    @property
    def states(self):
        """
        """
        return self.obj._states

    @property
    def key(self):
        """
        Returns the current state key
        """
        return self.obj._current_state_key

    @property
    def initial(self):
        """
        Returns the current state key
        """
        return self.obj._initial_state_key

    @property
    def default(self):
        """
        Returns the default state key
        """
        return self.obj._default_state_key

    def serialize(self, request):
        """
        Return a serialized value of the workflow state for the api access
        """
        return OrderedDict([
            ('name', force_text(self.name)),
            ('transitions', list(
                [
                    OrderedDict((
                        ('name', force_text(s.name)),
                        ('action', k),
                        ('url', reverse(
                            'djangobmf:moduleapi_%s_%s:workflow' % (
                                self.django_object._meta.app_label,
                                self.django_object._meta.model_name,
                            ),
                            format=None,
                            request=request,
                            kwargs={'pk': self.django_object.pk, 'transition': k},
                        )),
                    ))
                    for k, s in self.transitions(request.user)
                ]
            )),
            ('update', self.object.update),
            ('delete', self.object.delete),
        ])

    def transitions(self, user):
        """
        Show all transitions
        """
        return self.obj._from_here(self.django_object, user)

    def transition(self, via, user, silent=False):
        """
        Make a state transition for this object
        """
        transitions = dict(self.transitions(user))
        if via not in transitions:
            raise ValidationError(_("This transition is not valid"))

        success_url = self.obj._call(via, self.django_object, user)
        self.django_object.modified_by = user
        self.django_object.save()

        if not silent:
            activity_workflow.send(
                sender=self.django_object.__class__,
                instance=self.django_object,
                initial=self.initial,
                final=self.key,
            )

        return success_url

    def __str__(self):
        return six.text_type(self.obj._current_state.name)
