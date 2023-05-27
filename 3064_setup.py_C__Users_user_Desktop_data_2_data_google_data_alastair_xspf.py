#!/usr/bin/env python

from distutils.core import setup
from distutils.core import Command

class test(Command):
    description = "run automated tests"
    user_options = [
        ("tests=", None, "list of tests to run (default all)"),
        ("verbosity=", "v", "verbosity"),
        ]

    def initialize_options(self):
        self.tests = []
        self.verbosity = 1

    def finalize_options(self):
        if self.tests:
            self.tests = self.tests.split(",")
        if self.verbosity:
            self.verbosity = int(self.verbosity)

    def run(self):
        import os.path
        import glob
        import sys
        import unittest

        build = self.get_finalized_command('build')
        self.run_command ('build')
        sys.path.insert(0, build.build_purelib)
        sys.path.insert(0, build.build_platlib)

        names = []
        for filename in glob.glob("test/test_*.py"):
            name = os.path.splitext(os.path.basename(filename))[0]
            if not self.tests or name in self.tests:
                names.append("test." + name)

        tests = unittest.defaultTestLoader.loadTestsFromNames(names)
        t = unittest.TextTestRunner(verbosity=self.verbosity)
        t.run(tests)

setup(
    name="xspf",
    version="0.0.1",
    description="xspf generator for python ",
    url="https://www.github.com/alastair",
    py_modules=['xspf'],
    cmdclass={'test': test },
)


