""" 
Package for importing the Qt bindings (either PySide or PyQt), starting Qt application and
event loop.
    
Three things are handled by this package.

1)  Importing PyQT(4) or PySide. This is done in qt_importer.loadQt(). See its
    docstring for the details on how it decides between the two bindings.
    There is no difference here between IPython and the regular Python.
    
2)  Creating the QApplication instance (or getting the singleton if it already
    exists). Also no difference between IPython and the regular Python.
        
3)  Starting the event loop. 
    
    If IPython is not running, qApp.exec_() is called, which is blocking.

    The IPython.lib.guisupport.start_event_loop_qt4() function is used. If no 
    event loop is yet running, it will start a blocking event loop. If an event
    loop is running, start_event_loop_qt4() will do nothing and return. It is
    therefore non-blocking. This makes user interaction from the command
    line possible.
    
    The user can start an IPython event loop by calling the '%gui qt' magic command, 
    by starting IPython with the --qui=qt command line option, or by setting
    c.TerminalIPythonApp.gui = 'qt' in ~/.ipython/<profile>/ipython_config.py 
    
See also:
    http://ipython.readthedocs.org/en/stable/api/generated/IPython.lib.guisupport.html

Known issues:
    
1)  Starting; ipython --gui=qt main.py
    Since this will start a non-blocking event loop before calling main, the
    application exits as soon as it is created. Use the IPython -i option to
    stay in IPython after the script has finished. 
    So run: ipython --gui=qt -i main.py
    
2)  PyQT4 has two API versions: Python 2 uses API v1 by default, Python 3 
    uses v2 (PySide only implements the v2 API). The API version must be set 
    before PyQt4 is imported!
    
    This program is written for v2 so if v1 is already running, an error will
    occur. If you use the iptyhon --qui=qt command line option to start an 
    event loop (and make interaction from the command line possible), IPython-2
    will start API v1 if PyQt is configured. To force IPython-2 to use the 
    v2 API, the QT_API environment variable must be set to 'pyqt'. 
    
    This works, unfortunately IPython 4.0.0 contains a bug and raises the 
    following ImportError: No module named qt. As a work around you can, 
        1: Ignore the ImportError
        2: Import PyQt4 (or PySide) manually. In IPython type: import PyQt4.QtCore
        3: Start the event loop with: %gui qt
            
"""

from .bindings import QtCore, QtGui, ACTIVE_BINDINGS
from .QtCore import Qt, QtSignal, QtSlot
from .app import get_qapp, get_qsettings, start_qt_event_loop

