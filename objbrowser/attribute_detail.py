""" Module that defines AttributeDetail
"""
from __future__ import absolute_import

import logging, inspect, types, pprint

logger = logging.getLogger(__name__)


class AttributeDetail(object):
    """ Determines how an object attribute is rendered in a table column
    """ 
    def __init__(self, name,
                 doc = "<no help available>",  
                 data_fn = None):

        if not callable(data_fn):
            raise ValueError("data_fn for {!r} must be function(object)->string. Got: {}"
                             .format(name, data_fn))
            
        self.name = name
        self.doc = doc
        self.data_fn = data_fn
        

###################
# Data functions ##
###################

PRETTY_PRINTER = pprint.PrettyPrinter(indent=4)


def obj_doc_str(obj):
    """ Returns the doc string of an object
    """
    try:
        return obj.__doc__
    except AttributeError:
        return '<no doc string found>'
                    
def obj_get_file_name(obj):
    """ Returns the file name that defines an object
    """
    try:
        return inspect.getfile(obj)
    except TypeError:
        return ''
                    
def obj_get_module_name(obj):
    """ Returns the module name that defines an object
    """
    module = inspect.getmodule(obj)
    if module:
        return module.__name__
    else:
        return ''
        
def obj_get_source_file_name(obj):
    """ Returns the Python source file name that defines an object
    """
    try:
        return inspect.getsourcefile(obj)
    except TypeError:
        return ''                
        
def obj_get_source_lines(obj):
    """ Returns the string representation of a list of source code lines of an object 
    """
    try:
        return repr(inspect.getsourcelines(obj))
    except TypeError:
        return ''        
    
def obj_get_source(obj):
    """ Returns source code of an object 
    """
    try:
        return inspect.getsource(obj)
    except TypeError:
        return ''
        

#######################
# Column definitions ##
#######################


ATTR_DETAIL_STR = AttributeDetail('str', 
        doc     = "The string representation of the object using the str() function.",
        #data_fn = str) 
        data_fn = lambda(obj): str(obj)) 
        
ATTR_DETAIL_REPR = AttributeDetail('repr', 
        doc     = "The string representation of the object using the repr() function.", 
        data_fn = lambda(obj): repr(obj)) 
        
ATTR_DETAIL_PRETTY_PRINT = AttributeDetail('pretty print', 
        doc     = "Pretty printed representation of the object using the pprint module.", 
        data_fn = PRETTY_PRINTER.pformat) 
        
ATTR_DETAIL_DOC_STRING = AttributeDetail('doc string', 
        doc     = "The object's doc string", 
        data_fn = obj_doc_str) 
        
ATTR_DETAIL_GET_DOC = AttributeDetail('inspect.getdoc', 
        doc     = "The objects doc string cleaned up by inspect.getdoc()", 
        data_fn = inspect.getdoc) 
        
ATTR_DETAIL_GET_COMMENTS = AttributeDetail('inspect.getcomments', 
        doc     = "Comments above the object's definition retrieved using inspect.getcomments()", 
        data_fn = inspect.getcomments) 
        
ATTR_DETAIL_GET_FILE = AttributeDetail('inspect.getfile', 
        doc     = "The file where the object is defined retrieved using inspect.getfile()", 
        data_fn = obj_get_file_name) 
        
ATTR_DETAIL_GET_MODULE = AttributeDetail('inspect.getmodule', 
        doc     = "The module where the object is defined retrieved using inspect.module()", 
        data_fn = obj_get_module_name) 
        
ATTR_DETAIL_GET_SOURCE_FILE = AttributeDetail('inspect.getsourcefile', 
        doc     = "The Python file where the object is defined retrieved using inspect.getfile()", 
        data_fn = obj_get_source_file_name) 
        
ATTR_DETAIL_GET_SOURCE_LINES = AttributeDetail('inspect.getsourcelines', 
        doc     = "Uses inspect.getsourcelines() to get a list of source lines for the object", 
        data_fn = obj_get_source_lines) 
        
ATTR_DETAIL_GET_SOURCE = AttributeDetail('inspect.getsource', 
        doc     = "The source code of an object retrieved using inspect.getsource()", 
        data_fn = obj_get_source) 
        

ALL_ATTR_DETAILS = (ATTR_DETAIL_STR, 
                    ATTR_DETAIL_REPR,
                    ATTR_DETAIL_PRETTY_PRINT,
                    ATTR_DETAIL_DOC_STRING, 
                    ATTR_DETAIL_GET_DOC, 
                    ATTR_DETAIL_GET_COMMENTS, 
                    ATTR_DETAIL_GET_FILE, 
                    ATTR_DETAIL_GET_MODULE, 
                    ATTR_DETAIL_GET_SOURCE_FILE, 
                    ATTR_DETAIL_GET_SOURCE_LINES, 
                    ATTR_DETAIL_GET_SOURCE)

DEFAULT_ATTR_DETAILS = (ATTR_DETAIL_STR, 
                        ATTR_DETAIL_REPR,
                        ATTR_DETAIL_PRETTY_PRINT,
                        ATTR_DETAIL_DOC_STRING, 
                        ATTR_DETAIL_GET_DOC, 
                        ATTR_DETAIL_GET_COMMENTS, 
                        ATTR_DETAIL_GET_FILE, 
                        ATTR_DETAIL_GET_MODULE, 
                        ATTR_DETAIL_GET_SOURCE_FILE, 
                        ATTR_DETAIL_GET_SOURCE_LINES, 
                        ATTR_DETAIL_GET_SOURCE)

