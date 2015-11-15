""" objbrowser package
"""
__all__ = ['browse', '__version__']

import sys, logging #, pprint, inspect
logger = logging.getLogger(__name__)

from objbrowser.objectbrowser import ObjectBrowser
from objbrowser.qtimp.app import handleException
from objbrowser.version import PROGRAM_VERSION as __version__
from objbrowser.version import DEBUGGING

if DEBUGGING:
    logger.debug("Overriding Python excepthook.")
    sys.excepthook = handleException

def browse(*args, **kwargs):
    """ Opens and executes an ObjectBrowser window
    """
    ObjectBrowser.browse(*args, **kwargs)

    
    