""" 
    Example that demonstrates inspecting a MatPlotLib Figure.
"""
from __future__ import print_function

import sys, logging
import numpy as np


from objbrowser import browse, logging_basic_config

logger = logging.getLogger(__name__)

        
def main():
    """ Main program to test stand alone 
    """
    logging_basic_config('DEBUG')
    logger.info('Started example')

    #x = np.arange(24).reshape(6, 4)
    x = np.zeros((2,),dtype=('i4,f4,a10'))
    x[:] = [(1,2.,'Hello'),(2,3.,"World")]
    
    exit_code = browse(x.dtype.fields, obj_name='x.dtype.fields', show_special_attributes=False)

    logging.info('Done example')
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
