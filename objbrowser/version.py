""" Version info for objbrowser
"""
import os, sys
import objbrowser.qtpy, objbrowser.qtpy._version

DEBUGGING = False

PROGRAM_NAME = 'objbrowser'
PROGRAM_VERSION = '1.2.0'
PROGRAM_URL = 'https://github.com/titusjan/objbrowser'
PROGRAM_DIRECTORY = os.path.abspath(os.path.dirname(__file__))

PYTHON_VERSION = "%d.%d.%d" % (sys.version_info[0:3])
QT_API = objbrowser.qtpy.API
QT_API_NAME = objbrowser.qtpy.API_NAME
QTPY_VERSION = '.'.join(map(str, objbrowser.qtpy._version.version_info))




