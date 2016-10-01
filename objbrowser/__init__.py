""" objbrowser package
"""
__all__ = ['browse', '__version__', 'logging_basic_config']

import sys, logging #, pprint, inspect
logger = logging.getLogger(__name__)

from objbrowser.objectbrowser import ObjectBrowser
from objbrowser.qtimp.app import handleException
from objbrowser.version import PROGRAM_VERSION as __version__
from objbrowser.version import DEBUGGING
from objbrowser.utils import logging_basic_config

if DEBUGGING:
    logging_basic_config('DEBUG')
    logger.warn("DEBUGGING flag is on")
    logger.debug("Overriding Python excepthook.")
    sys.excepthook = handleException

def browse(*args, **kwargs):
    """ Opens and executes an ObjectBrowser window
    """
    ObjectBrowser.browse(*args, **kwargs)

    
    