""" Version info for objbrowser
"""
import os, sys
import qtpy, qtpy._version

DEBUGGING = False

PROGRAM_NAME = 'objbrowser'
PROGRAM_VERSION = '1.1.0'
PROGRAM_URL = 'https://github.com/titusjan/objbrowser'
PROGRAM_DIRECTORY = os.path.abspath(os.path.dirname(__file__))

PYTHON_VERSION = "%d.%d.%d" % (sys.version_info[0:3])
QT_API = qtpy.API
QTPY_VERSION = '.'.join(map(str, qtpy._version.version_info))




