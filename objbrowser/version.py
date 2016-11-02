""" Version info for objbrowser
"""
import os, sys

DEBUGGING = False

PROGRAM_NAME = 'objbrowser'
PROGRAM_VERSION = '1.2.1rc1'
PROGRAM_URL = 'https://github.com/titusjan/objbrowser'
PROGRAM_DIRECTORY = os.path.abspath(os.path.dirname(__file__))

PYTHON_VERSION = "%d.%d.%d" % (sys.version_info[0:3])

try:
    import objbrowser.qtpy, objbrowser.qtpy._version
except Exception:
    QT_API = "<NOT-FOUND>"
    QT_API_NAME = "<NOT-FOUND>"
    QTPY_VERSION = "<NOT-FOUND>"
else:
    QT_API = objbrowser.qtpy.API
    QT_API_NAME = objbrowser.qtpy.API_NAME
    QTPY_VERSION = '.'.join(map(str, objbrowser.qtpy._version.version_info))




