""" 
   Example that demonstrates inspecting module contents.
   
   Also demonstrates starting two browser windows simultaneously.
"""
from __future__ import print_function

import sys, logging

from objbrowser import logging_basic_config
from objbrowser.objectbrowser import ObjectBrowser

logger = logging.getLogger(__name__)

def call_errno_test():
    """ Test procedure. 
    """
    import errno
    from six.moves import builtins
    
    ObjectBrowser.create_browser(errno, 'errno')
    ObjectBrowser.create_browser(builtins, 'builtins')
    exit_code = ObjectBrowser.execute()
    return exit_code
    
        
def main():
    """ Main program to test stand alone 
    """
    logging_basic_config('DEBUG')
    logger.info('Started example')
    exit_code = call_errno_test()
    logging.info('Done example')
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
