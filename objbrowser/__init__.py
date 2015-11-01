""" objbrowser package
"""
__all__ = ['browse', '__version__']

import sys, os, logging #, pprint, inspect

from objbrowser.version import PROGRAM_VERSION as __version__
from objbrowser.application import getGlobalApp


logger = logging.getLogger(__name__)


def browse(*args, **kwargs):
    """ Opens and executes an ObjectBrowser window
    """
    application = getGlobalApp()
    application.create_browser(*args, **kwargs)
    application.execute()
    