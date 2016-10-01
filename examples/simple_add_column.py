""" 
    Example that demonstrates the simples way of defining your own columns.
    See also add_columns.py
"""
from __future__ import print_function

import sys, logging
from math import sqrt
from PySide.QtCore import Qt

from objbrowser import browse, logging_basic_config
from objbrowser.attribute_model import (AttributeModel, 
                                        DEFAULT_ATTR_COLS, safe_data_fn)

logger = logging.getLogger(__name__)

   
def my_browse(*args, **kwargs):
    """ Creates and starts an ObjectBrowser with added sqrt column.
    """
    sqrt_attr_model = AttributeModel('sqrt', 
        doc         = "The sqrt of an object if it can be calculated", 
        data_fn     = safe_data_fn(sqrt),
        col_visible = True,
        width       = 120,   
        alignment   = Qt.AlignRight) 

    attribute_columns = list(DEFAULT_ATTR_COLS)
    attribute_columns.insert(5, sqrt_attr_model)
    
    return browse(*args, attribute_columns = attribute_columns, **kwargs)
    
  
def main():
    """ Main program 
    """
    logging_basic_config('DEBUG')
    logger.info('Started example')

    # define some local variables
    lst = range(-5, 5) 
    b = True
    i = 555 
    f = 6.2 
    c = 3.2j - 0.1
    m = -4
    n = None
    s = '44'
    z = 'zonk'
            
    exit_code = my_browse(locals(),  
                          show_callable_attributes=False,
                          show_special_attributes=False)

    logging.info('Done example')
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
    