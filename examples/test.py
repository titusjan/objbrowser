#!/usr/bin/env python
"""
   Test program that shows an object browser containing many types and variables.
"""
from __future__ import print_function

import sys, logging, six
import datetime as dt
from collections import OrderedDict
from objbrowser import browse
from objbrowser.utils import logging_basic_config
from objbrowser.attribute_model import ALL_ATTR_MODELS

logger = logging.getLogger(__name__)

MY_CONSTANT = 55
YOUR_CONSTANT = MY_CONSTANT
ANOTHER_CONSTANT = MY_CONSTANT * 2

def call_viewer_test():
    """ Test procedure. 
    """
    import types, os
    from os.path import join
    
    if 1:
        # In Python 3 there is no OldStyleClass anymore. The definition below will result in a 
        # new style class as well.
        class OldStyleClass: 
            """ An old style class (pre Python 2.2)
                See: http://docs.python.org/2/reference/datamodel.html#new-style-and-classic-classes
            """
            static_member = 'static_value'
            def __init__(self, s, i):
                'constructor'            
                self._member_str = s
                self.__member_int = i
                
        class NewStyleClass(object):
            """ A new style class (Python 2.2 and later). Note it inherits 'object'.
                See: http://docs.python.org/2/reference/datamodel.html#new-style-and-classic-classes
            """
            static_member = 'static_value'
            def __init__(self, s, i):
                'constructor'
                self._member_str = s
                self.__member_int = i
                
            @property
            def member_int(self):
                return self.__member_int
                
            @member_int.setter
            def member_int(self, value):
                self.__member_int = value
                
            def method(self):
                pass
         
            @staticmethod       
            def static_method(self):
                pass
            
            @classmethod       
            def class_method(self):
                pass
        
        old_style_object = OldStyleClass('member_value', 44)    
        new_style_object = NewStyleClass('member_value', -66)    

    # Some comments just above
    # the function definition.
    def my_function(param):
        "demo function"
        return param
    
    _copyright = types.__builtins__['copyright'] 
    
    x_plus_2 = lambda x: x+2
    
    Int = int
    a = 6
    b = 'seven'
    c = 8j + 3 # complex number
    d = {'4': 44, 's': 11, c: None}
    e = 2.718281828
    f_large = 7.77e14 # different str and repr?
    f_avogadro = 6.02214129e23
    ellip = Ellipsis
    my_slice = slice(None, 3, -1)
    n = None
    not_impl = NotImplemented
    tup = ('this', 'is', 'a tuple')
    lst = [4, '4', d, ['r', dir], main]
    my_set = set([3, 4, 4, 8])
    my_frozenset = frozenset([3, 4, 5, 6, 6])
    
    dict_regular = {'banana': 3, 'apple':4, 'pear': 1, 'orange': 2}
    dict_ordered = OrderedDict(sorted(dict_regular.items(), key=lambda t: t[1])) # sorted by value

    __dunder_dict_item__ = """A variable that begins and end with two underscores but is a
        dictionary item, opposed to an attribute. It should therefore always be displayed, even
        if the 'show __dunder_attributes__' view option is toggled off
    """

    dt_now = dt.datetime.now()
    date_now = dt.date(2014, 3, 23) 
    date_first = date_now.min
    date_last = date_now.max
    
    t = dt.time(13, 33, 1)
    
    try:
        import numpy as np
    except ImportError as ex:
        logger.warning(ex)
    else:
        arr = np.arange(24, dtype=np.uint16).reshape(8, 3)
        pi_16bit = np.float16(np.pi)

        # Datetime arrays
        daysInFeb2005 = np.arange('2005-02', '2005-03', dtype='datetime64[D]')

        # Structured arrays (http://docs.scipy.org/doc/numpy/user/basics.rec.html)
        datatype1 = np.dtype([('name', np.str_, 16), ('grade', np.float64)])
        structured_array = np.array([('Sarah', 8.0), ('John', 7.5)], dtype=datatype1)

        # Structured array with sub array
        # (http://docs.scipy.org/doc/numpy/reference/arrays.dtypes.html
        datatype2 = np.dtype([('name', np.str_, 16), ('grades', np.float64, (2,))])
        array_with_sub_array = np.array([('Sarah', (8.0, 7.0)), ('John', (6.0, 7.0))], dtype=datatype2)

    try:
        import serial
    except ImportError as ex:
        logger.warning(ex)
    else:
        # PySerial object. Does not work if the port/device is closed. I cannot fix this.
        ser = serial.Serial()

    
    # These will give error in the str() representation. 
    # I deliberately did not use string.encode('ascii', 'backslashreplace') to 
    # demonstrate the difference between str() and repr()
    u1 = six.unichr(40960) + u'ab\ncd' + six.unichr(1972)
    u2 = u"a\xac\u1234\u20ac\U00008000"
    u3 = u'all ASCII chars'
    multi_line_str = """hello\r\nworld
                        the\rend."""

    # TODO: LOOK at iterators and generators. E.g. beautiful soup

    browse(locals(), reset = False, # without obj_name
           show_dunder_attributes = None,
           show_callable_attributes = None)
    if 0: 
        browse(globals(), name = 'globals()',
               attribute_columns = ALL_ATTR_MODELS, 
               attribute_details = ALL_ATTR_MODELS[1:4])
        

    
        
def main():
    """ Main program to test stand alone 
    """
    logging_basic_config('DEBUG')
    logger.info('Started example')
    
    exit_code = call_viewer_test()
    
    logging.info('Done example')
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
