#!/usr/bin/env python
"""
    Example that demonstrates overriding the summary column
"""
from __future__ import print_function

import sys, logging, copy
from objbrowser import browse, logging_basic_config
from objbrowser.attribute_model import DEFAULT_ATTR_COLS, tio_summary

logger = logging.getLogger(__name__)

class MyPoint(object):
    """ Example class for representing a point
    """
    def __init__(self, x, y):
        """ Constructor
        """
        self.x = x
        self.y = y
                
    def __repr__(self):
        """ String representation
        """
        return "<MyPoint: x = {}, y = {}>".format(self.x, self.y)


def my_summary(tree_item):
    """ Returns (x, y) if the tree_item object is a point. 
        Otherwise uses the default summary
    """
    tio = tree_item.obj
    if isinstance(tio, MyPoint):
        return "({}, {})".format(tio.x, tio.y)
    else:
        return tio_summary(tree_item)


def my_browse(*args, **kwargs):
    """ Creates and starts an ObjectBrowser with modified summary column.
    """
    attribute_columns = copy.deepcopy(DEFAULT_ATTR_COLS)
    summary_column = [col for col in attribute_columns if col.name == 'summary'][0]
    summary_column.data_fn = my_summary
    return browse(*args, attribute_columns = attribute_columns, **kwargs)
    
            
def main():
    """ Main program
    """
    logging_basic_config('DEBUG')
    logger.info('Started example')

    my_list = range(5, 9)
    p1 = MyPoint(0.0, 0.0)
    p2 = MyPoint(-4, 1)
        
    exit_code = my_browse({'my_list': my_list, 'p1': p1, 'p2': p2},  
                          show_callable_attributes=False,
                          show_special_attributes=False, 
                          reset=True)

    logging.info('Done example')
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
