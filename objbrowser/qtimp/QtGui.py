""" Module that allows for importing qtimp.QtGui.*
"""
from .bindings import ACTIVE_BINDINGS, BINDINGS_PYQT, BINDINGS_PYSIDE

if ACTIVE_BINDINGS == BINDINGS_PYQT:
    from PyQt4.QtGui import * 
elif ACTIVE_BINDINGS == BINDINGS_PYSIDE:
    from PySide.QtGui import * 
else:
    raise ValueError("Invalid bindings: {}".format(ACTIVE_BINDINGS))
    