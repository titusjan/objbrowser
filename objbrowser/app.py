""" Module for IPython event loop integration.

Two things are handled by this module .

1)  Creating the QApplication instance (or getting the singleton if it already
    exists). Also no difference between IPython and the regular Python.

2)  Starting the event loop.

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

    Also IPython 5.0.0 and 5.1.0 contain a bug so it won't work there as well.
    See https://github.com/ipython/ipython/issues/9974. It is expected to be fixed
    in IPython 5.2.0
"""

import sys, logging, traceback
logger = logging.getLogger(__name__)

from qtpy import QtCore, QtWidgets
from objbrowser.version import DEBUGGING, PROGRAM_NAME


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
    return QtWidgets.QApplication.instance() is not None


def get_qapp(*args, **kwargs):
    """ Gets the global Qt application object. Creates one if it doesn't exist.
    """
    qApp = QtWidgets.QApplication.instance()
    if qApp:
        logger.debug("Returning existing QApplication")
        return qApp
    else:
        logger.debug("Creating new QApplication")
        return QtWidgets.QApplication(*args, **kwargs)
        
        
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
        elif version_info[0] == 5 and version_info[1] <= 1:
            # The is_event_loop_running_qt4 function is broken in IPython 5.0 and 5.1.
            # https://github.com/ipython/ipython/issues/9974
            logger.debug("Event loop integration does not work in IPython 5.0 and 5.1")
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
        if not QtWidgets.qApp:
            _app = QtWidgets.QApplication()
         
        msgBox = ResizeDetailsMessageBox()
        msgBox.setText("Bug: uncaught {}".format(exc_type.__name__))
        msgBox.setInformativeText(str(exc_value))
        lst = traceback.format_exception(exc_type, exc_value, exc_traceback)
        msgBox.setDetailedText("".join(lst))
        msgBox.setIcon(QtWidgets.QMessageBox.Warning)
        msgBox.exec_()
        sys.exit(1)



class ResizeDetailsMessageBox(QtWidgets.QMessageBox):
    """ Message box that enlarges when the 'Show Details' button is clicked.
        Can be used to better view stack traces. I could't find how to make a resizeable message
        box but this it the next best thing.

        Taken from:
        http://stackoverflow.com/questions/2655354/how-to-allow-resizing-of-qmessagebox-in-pyqt4
    """
    def __init__(self, detailsBoxWidth=700, detailBoxHeight=300, *args, **kwargs):
        """ Constructor
            :param detailsBoxWidht: The width of the details text box (default=700)
            :param detailBoxHeight: The heights of the details text box (default=700)
        """
        super(ResizeDetailsMessageBox, self).__init__(*args, **kwargs)
        self.detailsBoxWidth = detailsBoxWidth
        self.detailBoxHeight = detailBoxHeight


    def resizeEvent(self, event):
        """ Resizes the details box if present (i.e. when 'Show Details' button was clicked)
        """
        result = super(ResizeDetailsMessageBox, self).resizeEvent(event)

        details_box = self.findChild(QtWidgets.QTextEdit)
        if details_box is not None:
            #details_box.setFixedSize(details_box.sizeHint())
            details_box.setFixedSize(QtCore.QSize(self.detailsBoxWidth, self.detailBoxHeight))

        return result
