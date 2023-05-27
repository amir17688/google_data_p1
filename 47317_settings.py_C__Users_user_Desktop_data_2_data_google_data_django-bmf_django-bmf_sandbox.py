#!/usr/bin/python
# ex:set fileencoding=utf-8:

import os
import sys
import tempfile


BASE_DIR = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

DEBUG = True

INTERNAL_IPS = ('127.0.0.1',)
ALLOWED_HOSTS = ["127.0.0.1"]

# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Berlin'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_L10N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_I18N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

LANGUAGE_CODE = 'en'
LANGUAGES = (
    (u'de', 'German'),
    (u'en', 'English'),
    (u'ru', 'Russian'),
    (u'pl', 'Polish'),
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
)

ROOT_URLCONF = 'sandbox.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'sandbox.wsgi.application'

SECRET_KEY = 'djangobmf-secret-key'

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

TEST_PROJECT_APPS = (
    'djangobmf',
    'djangobmf.contrib.accounting',
    'djangobmf.contrib.address',
    'djangobmf.contrib.customer',
    'djangobmf.contrib.employee',
    'djangobmf.contrib.invoice',
    'djangobmf.contrib.position',
    'djangobmf.contrib.product',
    'djangobmf.contrib.project',
    'djangobmf.contrib.quotation',
    # 'djangobmf.contrib.shipment',
    # 'djangobmf.contrib.stock',
    'djangobmf.contrib.task',
    'djangobmf.contrib.taxing',
    'djangobmf.contrib.team',
    'djangobmf.contrib.timesheet',
    'djangobmf.currency.EUR',
    'djangobmf.currency.USD',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'rest_framework',
)

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# CACHE ===========================================================================

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake-439478'
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = '/media/'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "tests", "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': True,
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.core.context_processors.debug',
                'django.core.context_processors.i18n',
                'django.core.context_processors.media',
                'django.core.context_processors.static',
                'django.core.context_processors.tz',
                'django.core.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# === TRAVIS ------------------------------------------------------------------

if "TRAVIS" in os.environ:
    BMF_DOCUMENT_ROOT = tempfile.mkdtemp(prefix='djangobmf_')
    BMF_DOCUMENT_URL = '/documents/'

    CELERY_ALWAYS_EAGER = True  # deactivate celery

    INSTALLED_APPS += (
        'djangobmf',
    #   'celery',
    )

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
#           'ENGINE': 'django.db.backends.postgresql_psycopg2',
#           'NAME': 'djangobmf',
#           'USER': 'postgres',
#           'HOST': '',
#           'PORT': '',
        }
    }

# === DOCKER ------------------------------------------------------------------

elif "DOCKER" in os.environ:
    BMF_DOCUMENT_ROOT = os.path.join(BASE_DIR, "documents")
    BMF_DOCUMENT_URL = '/documents/'

    CELERY_RESULT_BACKEND = 'redis://redis:6379/0'

    INSTALLED_APPS += (
        'celery',
    )
    INSTALLED_APPS += TEST_PROJECT_APPS
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'postgres',
            'USER': 'postgres',
            'HOST': 'postgres',
            'PORT': '5432',
        }
    }
    BROKER_URL = 'redis://redis:6379/0'

# === Local Runtests ----------------------------------------------------------

elif "DJANGOBMF_RUNTESTS" in os.environ:
    BMF_DOCUMENT_ROOT = tempfile.mkdtemp(prefix='djangobmf_')
    BMF_DOCUMENT_URL = '/documents/'

    CELERY_ALWAYS_EAGER = True  # deactivate celery


    INSTALLED_APPS += (
        'celery',
        'djangobmf',
    )

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
        }
    }

# === Virtual environments ----------------------------------------------------

else:
    BMF_DOCUMENT_ROOT = os.path.join(BASE_DIR, "documents")
    BMF_DOCUMENT_URL = '/documents/'
    BMF_USE_CELERY = False

    INSTALLED_APPS += TEST_PROJECT_APPS

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '%s/database.sqlite' % BASE_DIR,
        }
    }

    # enable debug toolbar
    if 'runserver' in sys.argv:
        INSTALLED_APPS += (
            'debug_toolbar',
        )
        MIDDLEWARE_CLASSES += (
            'debug_toolbar.middleware.DebugToolbarMiddleware',
        )
        DEBUG_TOOLBAR_CONFIG = {
            'JQUERY_URL': None,
        }

# LOGGING =========================================================================

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S",
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console':{
             'level': 'DEBUG',
             'filters': ['require_debug_true'],
             'class': 'logging.StreamHandler',
             'formatter': 'verbose',
         },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'djangobmf': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    }
}

# === OVERWRITE WITH LOCAL SETTINGS -------------------------------------------

try:
    from settings_local import *
except:
    pass
