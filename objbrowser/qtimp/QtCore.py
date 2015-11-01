""" Module that allows for importing qtimp.QtCore.*
"""
from .bindings import ACTIVE_BINDINGS, BINDINGS_PYQT, BINDINGS_PYSIDE

if ACTIVE_BINDINGS == BINDINGS_PYQT:
    from PyQt4.QtCore import *
    del pyqtSignal
    del pyqtSlot 
    from PyQt4.QtCore import pyqtSignal as QtSignal
    from PyQt4.QtCore import pyqtSlot as QtSlot 
        
elif ACTIVE_BINDINGS == BINDINGS_PYSIDE:
    from PySide.QtCore import * 
    del Signal
    del Slot
    from PySide.QtCore import Signal as QtSignal
    from PySide.QtCore import Slot as QtSlot
    
else:
    raise ValueError("Invalid bindings: {}".format(ACTIVE_BINDINGS))
    