""" Application singleton object
    
"""
import sys, logging

logger = logging.getLogger(__name__)

from objbrowser.qtimp import get_qapp

from objbrowser.objectbrowser import ObjectBrowser
from objbrowser.version import PROGRAM_NAME, PROGRAM_VERSION

_APP_SINGLETON = None
        
        
class Application(object):
    """ Class (meant to be a singleton) that maintains a list of browser windows and
        keeps a reference to the Qt application
    """
    
    def __init__(self):
        """ Initializes the Qt application
        """
        self.browsers = []
        self.q_app = get_qapp(sys.argv)
        self.q_app.setApplicationName(PROGRAM_NAME)
        self.q_app.setApplicationVersion(PROGRAM_VERSION)
        self.q_app.setOrganizationName("titusjan")
        self.q_app.setOrganizationDomain("titusjan.nl")    

        
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
        exit_code = self.q_app.exec_()
        return exit_code
        

def getGlobalApp():
    """ Returns the Application singleton.
    """
    global _APP_SINGLETON
    if _APP_SINGLETON is None:
        _APP_SINGLETON = Application()
    return _APP_SINGLETON
        
        
        