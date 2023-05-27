#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright (C) 2013, Cameron White
from github import Github
from github import MainClass
from github.Authorization import Authorization
from github.Requester import Requester
import re
import argparse
import ConfigParser

SECTION = 'accounts'

def store_token(file_path, account_type, username, token):
    
    config = ConfigParser.ConfigParser()

    config.read(file_path)

    if not config.has_section(SECTION):
        config.add_section(SECTION)

    config.set(
        SECTION, 
        '{}.{}.token'.format(account_type, username),
        token
    )

    with open(file_path, 'wb') as configfile:
        config.write(configfile)

def load_token(file_path, account_type, username):

    config = ConfigParser.ConfigParser()

    config.read(file_path)
    
    option = '{}.{}.token'.format(account_type, username)

    token = None
    if config.has_option(SECTION, option):
        token = config.get(SECTION, option)

    return token

def generate_tokens(file_path, account_type):
    
    config = ConfigParser.ConfigParser()

    config.read(file_path)
    
    if config.has_section(SECTION):
        for option, value in config.items(SECTION):
            if re.search('^\w+\.\w+\.token$', option):
                account_type, username, _ = option.split('.')
                yield account_type, username, value

def gitignore_types(github):
    for i in github.get_user('github')\
                   .get_repo('gitignore')\
                   .get_git_tree('master')\
                   .tree:
        t = re.split('.gitignore', i.path)
        if t[0] is not '':
            yield t[0]
