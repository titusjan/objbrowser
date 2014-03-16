""" Module that defines AttributeModel
"""
from __future__ import absolute_import

from PySide.QtCore import Qt

import logging, inspect, types, string, pprint

logger = logging.getLogger(__name__)

SMALL_COL_WIDTH = 120
MEDIUM_COL_WIDTH = 200

class AttributeModel(object):
    """ Determines how an object attribute is rendered in a table column or details pane
    """ 
    def __init__(self, name,
                 doc = "<no help available>",  
                 data_fn = None,  
                 col_visible = True, 
                 width = MEDIUM_COL_WIDTH,
                 alignment = Qt.AlignLeft):
        """
            Constructor
            
            :param name: name used to describe the attribute
            :type name: string
            :param doc: short string documenting the attribute
            :type doc: string
            :param data_fn: function that calculates the value shown in the UI
            :type  data_fn: function(TreeItem_ to string.
            :param col_visible: if True, the attribute is col_visible by default in the table
            :type col_visible: bool
            :param width: default width in the attribute table
            :type with: int
            :param alignment: alignment of the value in the table
            :type alighment: Qt.AlignmentFlag 
        """

        if not callable(data_fn):
            raise ValueError("data_fn must be function(TreeItem)->string")
            
        self.name = name
        self.doc = doc
        self.data_fn = data_fn
        self.col_visible = col_visible
        self.width = width
        self.alignment = alignment
        
    
    @property
    def settings_name(self):
        """ The name where spaces are replaced by underscores 
        """
        sname = self.name.replace(' ', '_')
        return sname.translate(None, string.punctuation).translate(None, string.whitespace)


###################
# Data functions ##
###################


PRETTY_PRINTER = pprint.PrettyPrinter(indent=4)

ALL_PREDICATES = (inspect.ismodule, inspect.isclass, inspect.ismethod,
                  inspect.isfunction, inspect.isgeneratorfunction, inspect.isgenerator,
                  inspect.istraceback, inspect.isframe, inspect.iscode,
                  inspect.isbuiltin, inspect.isroutine, inspect.isabstract,
                  inspect.ismethoddescriptor, inspect.isdatadescriptor, inspect.isgetsetdescriptor,
                  inspect.ismemberdescriptor) 

def tio_predicates(tree_item):
    """ Returns the inspect module predicates that are true for this object
    """
    tio = tree_item.obj
    predicates = [pred.__name__ for pred in ALL_PREDICATES if pred(tio)]
    return ", ".join(predicates)


def tio_simple_value(tree_item):
    """ Returns a the string representation of the tree_item.obj if it has a 'simple' type.
        
        That is: the type is a scalar or a string, not a compound such as a list.
    """
    tio = tree_item.obj
    tio_type = type(tio)
    if tio_type in (types.BooleanType, types.FloatType, types.IntType, types.NoneType):
        return repr(tio)
    elif tio_type == types.StringType:
        return repr(tio.encode('string_escape'))
    elif tio_type == types.UnicodeType:
        return repr(tio.encode('unicode_escape'))
    else:
        return ""
    

def tio_length(tree_item):
    """ Returns a the length the tree_item.obj if it has one
    """
    tio = tree_item.obj
    if hasattr(tio, "__len__"):
        try:
            return len(tio)
        except:
            logger.error("No len() for: {}".format(tio))
            return ""
    else:
        return ""
    
def tio_is_callable(tree_item):
    "Returns True if the tree item object is callable"
    return str(hasattr(tree_item.obj, "__call__"))    


def tio_doc_str(tree_item):
    """ Returns the doc string of an object
    """
    tio = tree_item.obj
    try:
        return tio.__doc__
    except AttributeError:
        return '<no doc string found>'
          
                    
def tio_get_file_name(tree_item):
    """ Returns the file name that defines an object
    """
    tio = tree_item.obj
    try:
        return inspect.getfile(tio)
    except TypeError:
        return ''
               
                    
def tio_get_module_name(tree_item):
    """ Returns the module name that defines an object
    """
    tio = tree_item.obj
    module = inspect.getmodule(tio)
    if module:
        return module.__name__
    else:
        return ''

        
def tio_get_source_file_name(tree_item):
    """ Returns the Python source file name that defines an object
    """
    tio = tree_item.obj
    try:
        return inspect.getsourcefile(tio)
    except TypeError:
        return ''                

        
def tio_get_source_lines(tree_item):
    """ Returns the string representation of a list of source code lines of an object 
    """
    tio = tree_item.obj
    try:
        return repr(inspect.getsourcelines(tio))
    except TypeError:
        return ''        

    
def tio_get_source(tree_item):
    """ Returns source code of an object 
    """
    tio = tree_item.obj
    try:
        return inspect.getsource(tio)
    except TypeError:
        return ''

#######################
# Column definitions ##
#######################

ATTR_MODEL_PATH = AttributeModel('path', 
    doc         = "A path to the data: e.g. var[1]['a'].item", 
    data_fn     = lambda(tree_item): tree_item.obj_path if tree_item.obj_path else '<root>', 
    col_visible = True,  
    width       = MEDIUM_COL_WIDTH, 
    alignment   = Qt.AlignLeft) 

ATTR_MODEL_NAME = AttributeModel('name', 
    doc         = "The name of the object.", 
    data_fn     = lambda(tree_item): tree_item.obj_name if tree_item.obj_name else '<root>',
    col_visible = True,  
    width       = MEDIUM_COL_WIDTH, 
    alignment   = Qt.AlignLeft) 

ATTR_MODEL_VALUE = AttributeModel('value', 
    doc         = "The value of the object for atomic objects (int, str, etc)", 
    data_fn     = tio_simple_value,
    col_visible = True,  
    width       = MEDIUM_COL_WIDTH, 
    alignment   = Qt.AlignLeft) 

ATTR_MODEL_TYPE = AttributeModel('type', 
    doc         = "Type of the object determined using the builtin type() function", 
    data_fn     = lambda(tree_item): str(type(tree_item.obj)),
    col_visible = False,  
    width       = MEDIUM_COL_WIDTH, 
    alignment   = Qt.AlignLeft) 

ATTR_MODEL_CLASS = AttributeModel('type name', 
    doc         = "The name of the class of the object via obj.__class__.__name__", 
    data_fn     = lambda(tree_item): type(tree_item.obj).__name__,
    col_visible = True,  
    width       = MEDIUM_COL_WIDTH, 
    alignment   = Qt.AlignLeft) 

ATTR_MODEL_CALLABLE = AttributeModel('callable', 
    doc         = "The if the is callable (e.g. a function or a method)", 
    data_fn     = tio_is_callable, 
    col_visible = True,  
    width       = SMALL_COL_WIDTH,
    alignment   = Qt.AlignLeft) 

ATTR_MODEL_LENGTH   = AttributeModel('length', 
    doc         = "The length of the object using the len() function", 
    data_fn     = tio_length, 
    col_visible = False,  
    width       = SMALL_COL_WIDTH,
    alignment   = Qt.AlignLeft) 

ATTR_MODEL_ID = AttributeModel('id', 
    doc         = "The identifier of the object with calculated using the id() function", 
    data_fn     = lambda(tree_item): "0x{:X}".format(id(tree_item.obj)), 
    col_visible = False,  
    width       = SMALL_COL_WIDTH,
    alignment   = Qt.AlignRight) 

ATTR_MODEL_PRED = AttributeModel('predicates', 
    doc         = "Predicates from the inspect module" ,
    data_fn     = tio_predicates, 
    col_visible = False,  
    width       = MEDIUM_COL_WIDTH, 
    alignment   = Qt.AlignLeft) 

ATTR_MODEL_STR = AttributeModel('str', 
    doc         = "The string representation of the object using the str() function.",
    data_fn     = lambda(tree_item): str(tree_item.obj), 
    col_visible = True,  
    width       = MEDIUM_COL_WIDTH, 
    alignment   = Qt.AlignLeft) 
 
ATTR_MODEL_REPR = AttributeModel('repr', 
    doc         = "The string representation of the object using the repr() function.", 
    data_fn     = lambda(tree_item): repr(tree_item.obj),         
    col_visible = True,  
    width       = MEDIUM_COL_WIDTH, 
    alignment   = Qt.AlignLeft)
        
ATTR_MODEL_PRETTY_PRINT = AttributeModel('pretty print', 
    doc         = "Pretty printed representation of the object using the pprint module.", 
    data_fn     = lambda(tree_item): PRETTY_PRINTER.pformat(tree_item.obj),         
    col_visible = False,  
    width       = MEDIUM_COL_WIDTH, 
    alignment   = Qt.AlignLeft) 
        
ATTR_MODEL_DOC_STRING = AttributeModel('doc string', 
    doc         = "The object's doc string", 
    data_fn     = tio_doc_str,         
    col_visible = False,  
    width       = MEDIUM_COL_WIDTH, 
    alignment   = Qt.AlignLeft)
        
ATTR_MODEL_GET_DOC = AttributeModel('inspect.getdoc', 
    doc         = "The objects doc string cleaned up by inspect.getdoc()", 
    data_fn     = lambda(tree_item): inspect.getdoc(tree_item.obj),         
    col_visible = False,  
    width       = MEDIUM_COL_WIDTH, 
    alignment   = Qt.AlignLeft)
        
ATTR_MODEL_GET_COMMENTS = AttributeModel('inspect.getcomments', 
    doc         = "Comments above the object's definition retrieved using inspect.getcomments()", 
    data_fn     = lambda(tree_item): inspect.getcomments(tree_item.obj),         
    col_visible = False,  
    width       = MEDIUM_COL_WIDTH, 
    alignment   = Qt.AlignLeft)
        
ATTR_MODEL_GET_FILE = AttributeModel('inspect.getfile', 
    doc         = "The file where the object is defined retrieved using inspect.getfile()", 
    data_fn     = tio_get_file_name,         
    col_visible = False,  
    width       = MEDIUM_COL_WIDTH, 
    alignment   = Qt.AlignLeft)
        
ATTR_MODEL_GET_MODULE = AttributeModel('inspect.getmodule', 
    doc         = "The module where the object is defined retrieved using inspect.module()", 
    data_fn     = tio_get_module_name,         
    col_visible = False,  
    width       = MEDIUM_COL_WIDTH, 
    alignment   = Qt.AlignLeft) 
        
ATTR_MODEL_GET_SOURCE_FILE = AttributeModel('inspect.getsourcefile', 
    doc         = "The Python file where the object is defined retrieved using inspect.getfile()", 
    data_fn     = tio_get_source_file_name,         
    col_visible = False,  
    width       = MEDIUM_COL_WIDTH, 
    alignment   = Qt.AlignLeft)
        
ATTR_MODEL_GET_SOURCE_LINES = AttributeModel('inspect.getsourcelines', 
    doc         = "Uses inspect.getsourcelines() to get a list of source lines for the object", 
    data_fn     = tio_get_source_lines,         
    col_visible = False,  
    width       = MEDIUM_COL_WIDTH, 
    alignment   = Qt.AlignLeft)
        
ATTR_MODEL_GET_SOURCE = AttributeModel('inspect.getsource', 
    doc         = "The source code of an object retrieved using inspect.getsource()", 
    data_fn     = tio_get_source,         
    col_visible = False,  
    width       = MEDIUM_COL_WIDTH, 
    alignment   = Qt.AlignLeft) 
        

ALL_ATTR_MODELS = (
    ATTR_MODEL_PATH, 
    ATTR_MODEL_NAME,
    ATTR_MODEL_VALUE,
    ATTR_MODEL_STR, 
    ATTR_MODEL_REPR,    
    ATTR_MODEL_TYPE, 
    ATTR_MODEL_CLASS, 
    ATTR_MODEL_CALLABLE, 
    ATTR_MODEL_LENGTH, 
    ATTR_MODEL_ID, 
    ATTR_MODEL_PRED,
    ATTR_MODEL_STR, 
    ATTR_MODEL_REPR,
    ATTR_MODEL_PRETTY_PRINT,
    ATTR_MODEL_DOC_STRING, 
    ATTR_MODEL_GET_DOC, 
    ATTR_MODEL_GET_COMMENTS, 
    ATTR_MODEL_GET_FILE, 
    ATTR_MODEL_GET_MODULE, 
    ATTR_MODEL_GET_SOURCE_FILE, 
    ATTR_MODEL_GET_SOURCE_LINES, 
    ATTR_MODEL_GET_SOURCE)

DEFAULT_ATTR_COLS = (
    ATTR_MODEL_PATH, 
    ATTR_MODEL_NAME,
    ATTR_MODEL_VALUE,
    ATTR_MODEL_STR, 
    ATTR_MODEL_REPR,    
    ATTR_MODEL_TYPE, 
    ATTR_MODEL_CLASS, 
    ATTR_MODEL_CALLABLE, 
    ATTR_MODEL_LENGTH, 
    ATTR_MODEL_ID, 
    ATTR_MODEL_PRED)

DEFAULT_ATTR_DETAILS = (
    ATTR_MODEL_STR, 
    ATTR_MODEL_REPR,
    ATTR_MODEL_PRETTY_PRINT,
    #ATTR_MODEL_DOC_STRING,  # not used, too similar to ATTR_MODEL_GET_DOC
    ATTR_MODEL_GET_DOC, 
    ATTR_MODEL_GET_COMMENTS, 
    ATTR_MODEL_GET_FILE, 
    ATTR_MODEL_GET_MODULE, 
    ATTR_MODEL_GET_SOURCE_FILE, 
    #ATTR_MODEL_GET_SOURCE_LINES, # not used, ATTR_MODEL_GET_SOURCE is better
    ATTR_MODEL_GET_SOURCE)
