""" Qt Application related functions.
"""

import sys, logging, traceback
logger = logging.getLogger(__name__)

from .bindings import QtCore, QtGui
from ..version import DEBUGGING, PROGRAM_NAME


def in_ipython():
    """ Returns True if IPython is running, False for the regular Python.
    """
    try:
        from IPython.core.getipython import get_ipython
    except ImportError:
        return False
    else:
        return get_ipython() is not None


def qapp_exists():
    """ Returns true if a QApplicaiotn is already running
    """
    return QtGui.QApplication.instance() is not None


def get_qapp(*args, **kwargs):
    """ Gets the global Qt application object. Creates one if it doesn't exist.
    """
    qApp = QtGui.QApplication.instance()
    if qApp:
        logger.debug("Returning existing QApplication")
        return qApp
    else:
        logger.debug("Creating new QApplication")
        return QtGui.QApplication(*args, **kwargs)
        
        
def get_qsettings():
    """ Creates a QSettings object for this application.    
        We do not set the application and organization in the QApplication object to 
        prevent side-effects.
    """
    return QtCore.QSettings("titusjan.nl", PROGRAM_NAME)
            
    
def start_qt_event_loop(qApp):
    """ Starts the eventloop if it's not yet running.

        If the IPython event loop is active (and set to Qt) this function does nothing. The IPython 
        event loop will process Qt events as well so the user can continue to use the command 
        prompt together with the ObjectBrower. Unfortunately this behaviour is broken again in
        IPython 5, so there we fall back on the non-interactive event loop.
    """
    if in_ipython():
        from IPython import version_info
        logger.debug("IPython detected. Version info: {}".format(version_info))
        if version_info[0] < 4:
            logger.debug("Event loop integration not supported for IPython < 4")
        elif version_info[0] == 5:
            # The is_event_loop_running_qt4 function doesn't seem to work anymore.
            logger.debug("Event loop integration does not work in IPython 5")
        else:
            try:
                from IPython.lib.guisupport import is_event_loop_running_qt4, start_event_loop_qt4
                if is_event_loop_running_qt4(qApp):
                    logger.info("IPython event loop already running. GUI integration possible.")
                else:
                    # No gui integration
                    logger.info("Starting (non-interactive) IPython event loop")
                    start_event_loop_qt4(qApp) # exit code always 0
                return
            except Exception as ex:
                logger.warning("Unable to start IPython Qt event loop: {}".format(ex))
                logger.warning("Falling back on non-interactive event loop: {}".format(ex))

    logger.info("Starting (non-interactive) event loop")
    return qApp.exec_()


def handleException(exc_type, exc_value, exc_traceback):
    """ Causes the application to quit in case of an unhandled exception (as God intended)
        Shows an error dialog before quitting when not in debugging mode.
    """

    traceback.format_exception(exc_type, exc_value, exc_traceback)
    
    logger.critical("Bug: uncaught {}".format(exc_type.__name__), 
                    exc_info=(exc_type, exc_value, exc_traceback))
    if DEBUGGING:
        sys.exit(1)
    else:
        # Constructing a QApplication in case this hasn't been done yet.
        if not QtGui.qApp:
            _app = QtGui.QApplication()
         
        msgBox = QtGui.QMessageBox()
        msgBox.setText("Bug: uncaught {}".format(exc_type.__name__))
        msgBox.setInformativeText(str(exc_value))
        lst = traceback.format_exception(exc_type, exc_value, exc_traceback)
        msgBox.setDetailedText("".join(lst))
        msgBox.setIcon(QtGui.QMessageBox.Warning)
        msgBox.exec_()
        sys.exit(1)
        