""" Version info for objbrowser
"""
import os, sys

DEBUGGING = False

PROGRAM_NAME = 'objbrowser'
PROGRAM_VERSION = '1.3.0'
PROGRAM_URL = 'https://github.com/titusjan/objbrowser'
PROGRAM_DIRECTORY = os.path.abspath(os.path.dirname(__file__))

PYTHON_VERSION = "%d.%d.%d" % (sys.version_info[0:3])

try:
    import qtpy, qtpy._version
except Exception:
    QT_API = "<NOT-FOUND>"
    QT_API_NAME = "<NOT-FOUND>"
    QTPY_VERSION = "<NOT-FOUND>"
else:
    QT_API = qtpy.API
    QT_API_NAME = qtpy.API_NAME
    QTPY_VERSION = '.'.join(map(str, qtpy._version.version_info))




