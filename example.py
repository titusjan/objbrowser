""" 
   Program that shows the local Python environment using the inspect module
"""
from __future__ import print_function

import sys, logging
from PySide import QtCore, QtGui
from objbrowser import ObjectBrowser, logging_basic_config

logger = logging.getLogger(__name__)


def call_viewer_test():
    """ Test procedure. 
    """
    import types, sys
    
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
        
    # Some comments just above
    # the function definition.
    def my_function(param):
        'demo function'
        return param
    
    _copyright = types.__builtins__['copyright'] 
    
    old_style_object = OldStyleClass('member_value', 44)    
    new_style_object = NewStyleClass('member_value', -66)    
    
    x_plus_2 = lambda x: x+2
    
    d = {'4': 44, 's': 11}
    a = 6
    b = 'seven'
    n = None
    tup = ('this', 'is', 'a tuple')
    lst = [4, '4', d, ['r', dir], main]
    my_set = set([3, 4, 4, 8])
    my_frozenset = frozenset([3, 4, 5, 6, 6])
    #http://docs.python.org/2/howto/unicode.html
    u1 = unichr(40960) + u'ab\ncd' + unichr(1972)
    u2 = u"a\xac\u1234\u20ac\U00008000"
    u3 = u'no strange chars'
    multi_line_str = """ hello\nworld
                        the end."""
    
    obj_browser = ObjectBrowser(obj = locals())
    obj_browser.resize(1100, 600)
    obj_browser.show()
    
    return obj_browser # to keep a reference


def call_viewer_small_test():
    """ Test procedure. 
    """
    
    a = 6
    b = ['seven', 'eight']
        
    #obj_browser1 = ObjectBrowser(obj = globals())
    #obj_browser = ObjectBrowser(obj = obj_browser1, obj_name='obj_browser1')
    obj_browser = ObjectBrowser(obj =[5, 6, 'a', ['r', 2, []]], obj_name='locals()')
    
    obj_browser.resize(1000, 600)
    obj_browser.show()
    
    return obj_browser # to keep a reference

        
def main():
    """ Main program to test stand alone 
    """
    app = QtGui.QApplication(sys.argv)


    logging_basic_config('DEBUG')

    logger.info('Started example')
    _obj_browser1 = call_viewer_test() # to keep a reference
    #_obj_browser2 = call_viewer_small_test() # to keep a reference
    exit_code = app.exec_()
    logging.info('Done example')
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
