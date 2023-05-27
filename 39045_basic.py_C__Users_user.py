"""
This module is always imported during Maya's startup.  It is imported from
both the maya.app.startup.batch and maya.app.startup.gui scripts
"""

import maya.cmds as cmds
import atexit
import traceback
import os
import maya
import sys
import maya.utils as utils

def setupScriptPaths():
    """
    Add Maya-specific directories to sys.path
    """

    pass


def executeUserSetup():
    """
    Look for userSetup.py in the search path and execute it in the "__main__"
    namespace
    """

    pass



