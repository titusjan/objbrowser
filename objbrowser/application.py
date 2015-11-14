""" Application singleton object
    
"""
import sys, logging

logger = logging.getLogger(__name__)

from objbrowser.qtimp import get_qapp, start_qt_event_loop
from objbrowser.qtimp.app import handleException

from objbrowser.objectbrowser import ObjectBrowser
from objbrowser.version import DEBUGGING, PROGRAM_NAME, PROGRAM_VERSION

_APP_SINGLETON = None
        
        
class Application(object):
    """ Class (meant to be a singleton) that maintains a list of browser windows and
        keeps a reference to the Qt application
    """
    
    def __init__(self, setExceptHook=False):
        """ Initializes the Qt application.
        
            if setExceptHook is True (or the program is indebugging mode), the Python
            exception hook is overridden so that an unhandled exception causes the application
            to terminate.
        """
        self.browsers = []
        self.q_app = get_qapp(sys.argv)

        if DEBUGGING or setExceptHook:
            logger.debug("Overriding Python excepthook.")
            sys.excepthook = handleException
            
        
    def create_browser(self, *args, **kwargs):
        """ Creates an ObjectBrowser window
            The *args and **kwargs will be passed to the ObjectBrowser constructor
        """
        object_browser = ObjectBrowser(*args, **kwargs)
        object_browser.show()
        object_browser.raise_()
        self.browsers.append(object_browser)
        return object_browser
    
    
    def execute(self):
        """ Starts the Qt event loop.
        """
        exit_code = start_qt_event_loop(self.q_app)
        return exit_code
        

def getGlobalApp():
    """ Returns the Application singleton.
    """
    global _APP_SINGLETON
    if _APP_SINGLETON is None:
        _APP_SINGLETON = Application()
    return _APP_SINGLETON
        
        
        