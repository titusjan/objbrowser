""" 
   Example that demonstrates inspecting module contents.
   
   Also demonstrates starting two browser windows simultaneously.
"""
from __future__ import print_function

import sys, logging
from objbrowser import create_object_browser, execute, logging_basic_config

logger = logging.getLogger(__name__)

def call_errno_test():
    """ Test procedure. 
    """
    import errno, __builtin__
    
    # Keep the _module_browser and _builtin_browser references, 
    # otherwise the windows will be garbage collected.
    _module_browser = create_object_browser(errno, 'errno')
    _builtin_browser = create_object_browser(__builtin__, '__builtin__')
    exit_code = execute()
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
