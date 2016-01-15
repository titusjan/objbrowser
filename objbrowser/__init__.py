""" objbrowser package
"""

__all__ = ['browse', 'execute', 'create_object_browser', 'logging_basic_config']

import sys, os, logging, pprint, inspect
from PySide import QtCore, QtGui

from objbrowser.objectbrowser import ObjectBrowser
from objbrowser.version import PROGRAM_NAME, PROGRAM_VERSION

__version__ = PROGRAM_VERSION

logger = logging.getLogger(__name__)

def logging_basic_config(level = 'INFO'):
    """ Setup basic config logging. Useful for debugging to quickly setup a useful logger"""
    fmt = '%(filename)25s:%(lineno)-4d : %(levelname)-7s: %(message)s'
    logging.basicConfig(level=level, format=fmt)
    
    
def check_class(obj, target_class, allow_none = False):
    """ Checks that the  obj is a (sub)type of target_class. 
        Raises a TypeError if this is not the case.
    """
    if not isinstance(obj, target_class):
        if not (allow_none and obj is None):
            raise TypeError("obj must be a of type {}, got: {}"
                            .format(target_class, type(obj)))    


def get_qapplication_instance():
    """ Returns the QApplication instance. Creates one if it doesn't exist.
    """
    app = QtGui.QApplication.instance()

    if app is None:
        app = QtGui.QApplication(sys.argv)
    check_class(app, QtGui.QApplication)
    
    app.setApplicationName(PROGRAM_NAME)
    app.setApplicationVersion(PROGRAM_VERSION)
    app.setOrganizationName("titusjan")
    app.setOrganizationDomain("titusjan.nl")    
    
    return app


def create_object_browser(*args, **kwargs):
    """ Opens an ObjectBrowser window.
    """
    _app = get_qapplication_instance()
    object_browser = ObjectBrowser(*args, **kwargs)
    object_browser.show()
    return object_browser
                
def browse(*args, **kwargs):
    """ Opens and executes an ObjectBrowser window.
        If the env variable QT_API is set to 'pyside' and '%gui qt' run in
        IPython, this function will not block the session.
    """

    app = get_qapplication_instance()
    _object_browse = create_object_browser(*args, **kwargs)
    app.references = set()
    app.references.add(_object_browse)
    try:
        from IPython.lib.guisupport import start_event_loop_qt4
        start_event_loop_qt4(app)
    except ImportError:
        exit_code = app.exec_()
        logger.info("Object browser(s) done...")
    else:
        exit_code = 0
    return exit_code
