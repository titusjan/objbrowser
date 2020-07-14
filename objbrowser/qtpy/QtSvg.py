# -*- coding: utf-8 -*-
#
# Copyright © 2009- The Spyder Development Team
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)

"""
Provides QtSvg classes and functions.
"""

from objbrowser.qtpy import PYQT5, PYQT4, PYSIDE, PYSIDE2, PythonQtError


if PYQT5:
    from PyQt5.QtSvg import *
elif PYQT4:
    from PyQt4.QtSvg import *
elif PYSIDE2:
    from PySide2.QtSvg import *
elif PYSIDE:
    from PySide.QtSvg import *
else:
    raise PythonQtError('No Qt bindings could be found')
