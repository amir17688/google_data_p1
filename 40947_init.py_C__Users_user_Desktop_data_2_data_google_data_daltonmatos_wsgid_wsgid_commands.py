

from wsgid.core import Plugin
from wsgid.core.command import ICommand
import os
import sys
from wsgid.core.parser import CommandLineOption, BOOL


class CommandInit(Plugin):

    implements = [ICommand]

    def command_name(self):
        return 'init'

    def name_matches(self, cname):
        return "init" == cname

    def run(self, options, **kwargs):
        sys.stderr.write("Initializing wsgid app folder in {0}...\n".format(options.app_path))
        needed_folders = ['pid', 'pid/master', 'pid/worker', 'app', 'logs', 'plugins']
        self._create_if_not_exist(options.app_path)

        for folder in needed_folders:
            self._create_if_not_exist(os.path.join(options.app_path, folder))

    def extra_options(self):
        return [CommandLineOption(name='no-init', help='Turns off debug option', type=BOOL)]

    def _create_if_not_exist(self, path):
        if not os.path.exists(path):
            os.mkdir(path)
