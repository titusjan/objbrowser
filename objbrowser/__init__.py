""" objbrowser package
"""
__all__ = ['browse', '__version__', 'logging_basic_config']

import logging
import sys
import traceback

logger = logging.getLogger(__name__)

from objbrowser.version import PROGRAM_VERSION as __version__
from objbrowser.version import DEBUGGING

# Wrap the following code in an exception so that setup.py can still import the PROGRAM_VERSION
# even if PyQt/PySide is not installed.
try:
    import six
    import qtpy.QtCore as _QtCore
except Exception as ex:

    traceback.print_exc()

    sys.stderr.write("\n")
    sys.stderr.write("  The following packages are required to run objbrowser:\n")
    sys.stderr.write("      six\n")
    sys.stderr.write("      PySide or PyQt\n")
    sys.stderr.write("\n")
    sys.stderr.write("  Could not run objbrowser because: {}".format(ex))
    sys.stderr.write("\n")
else:

    from objbrowser.app import handleException
    from objbrowser.objectbrowser import ObjectBrowser
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

    
    