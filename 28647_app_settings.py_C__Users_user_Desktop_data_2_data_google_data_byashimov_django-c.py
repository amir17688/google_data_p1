import sys

from django.utils import six


# I know, it's ugly, but I just can't write:
# gettattr(settings, 'CONTROLCENTER_CHARTIST_COLORS', 'default')
# This is way better: app_settings.CHARTIST_COLORS
# TODO: move to separate project


def proxy(attr, default):
    def wrapper(self):
        # It has to be most recent,
        # to override settings in tests
        from django.conf import settings
        return getattr(settings, attr, default)
    # Do I need this?
    wrapper.__name__ = attr
    return property(wrapper)


class AppSettingsMeta(type):
    def __new__(mcs, name, bases, attrs):
        prefix = name.upper() + '_'
        for attr, value in attrs.items():
            if not attr.startswith('__'):
                attrs[attr] = proxy(prefix + attr, value)

        abstract = attrs.pop('__abstract__', False)
        cls = super(AppSettingsMeta, mcs).__new__(mcs, name, bases, attrs)

        if not abstract:
            # http://mail.python.org/pipermail/python-ideas/2012-May/
            # 014969.html
            ins = cls()
            ins.__name__ = ins.__module__
            sys.modules[ins.__module__] = ins
        return cls


class AppSettings(six.with_metaclass(AppSettingsMeta)):
    __abstract__ = True


class ControlCenter(AppSettings):
    DASHBOARDS = []
    CHARTIST_COLORS = 'default'
    SHARP = '#'
