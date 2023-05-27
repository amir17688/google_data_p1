#!/usr/bin/python
# ex:set fileencoding=utf-8:

from fabric.api import *
from fabric.contrib import files

import os

BASEDIR = os.path.dirname(env.real_fabfile)

PYTHON = BASEDIR + "/virtenv/bin/python"
MANAGE = BASEDIR + "/manage.py"

from djangobmf.demo import FIXTURES

APPS = [
    'accounting',
    'address',
    'customer',
    'employee',
    'invoice',
    'position',
    'product',
    'project',
    'quotation',
    'task',
    'taxing',
    'team',
    'timesheet',
]


@task
def test(fast=False):
    """
    Tests code with django unittests
    """
    with lcd(BASEDIR):
        if fast:
            local('virtenv/bin/coverage run runtests.py -v2 --failfast')
        else:
            local('virtenv/bin/coverage run runtests.py -v2')
        local('virtenv/bin/coverage report -m --skip-covered')


@task
def test_mod(app):
    with lcd(BASEDIR):
        local('virtenv/bin/coverage run runtests.py -v2 --contrib %(app)s' % {'app': app})
        local('virtenv/bin/coverage report -m --skip-covered --include="djangobmf/contrib/%(app)s/*"' % {'app': app})


@task
def test_core(module=""):
    with lcd(BASEDIR):
        local('virtenv/bin/coverage run runtests.py %s -v2 --nocontrib' % module)
        local('virtenv/bin/coverage report -m --skip-covered --omit="djangobmf/contrib/*"')


@task
def locale():
    with lcd(BASEDIR + '/djangobmf'):
        local('%s %s makemessages -l %s --domain django' % (PYTHON, MANAGE, 'en'))
        local('%s %s makemessages -l %s --domain djangojs' % (PYTHON, MANAGE, 'en'))
        check_locale()

    for app in APPS:
        with lcd(BASEDIR + '/djangobmf/contrib/' + app):
            local('%s %s makemessages -l %s --domain django' % (PYTHON, MANAGE, 'en'))
            check_locale()

    with lcd(BASEDIR):
        local('tx pull -a')

    with lcd(BASEDIR + '/djangobmf'):
        local('%s %s compilemessages' % (PYTHON, MANAGE))

    for app in APPS:
        with lcd(BASEDIR + '/djangobmf/contrib/' + app):
            local('%s %s compilemessages' % (PYTHON, MANAGE))

    puts("Dont forget to run 'tx push -s' to push new source files")

def check_locale():
    numstat = local('git diff --numstat locale', quiet)
    for stats in numstat.split('\n'):
        insertions, deletions, file = stats.split('\t')
        if insertions == '1' and deletions == '1' and file[-3:] == '.po':
            with lcd(BASEDIR):
                local('git checkout -- %s' % file)

@task
def make(data=''):
  """
  """
  with lcd(BASEDIR):
    local('rm -f sandbox/database.sqlite')
    local('%s %s migrate --noinput' % (PYTHON, MANAGE))
    if not data:
        local('%s %s loaddata %s' % (PYTHON, MANAGE, ' '.join(FIXTURES)))
    else:
        local('%s %s loaddata fixtures/users.json' % (PYTHON, MANAGE))


@task
def start():
  """
  """
  with lcd(BASEDIR):
    local('%s %s runserver 8000' % (PYTHON, MANAGE))


@task
def shell():
  """
  """
  local('%s %s shell' % (PYTHON, MANAGE))
