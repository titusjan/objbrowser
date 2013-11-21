""" Module that defines AttributeColumn
"""
from __future__ import absolute_import

from PySide.QtCore import Qt

import logging, inspect, types, string

logger = logging.getLogger(__name__)


SMALL_COL_WIDTH = 120
MEDIUM_COL_WIDTH = 200

class AttributeColumn(object):
    """ Determines how an object attribute is rendered in a table column
    """ 
    def __init__(self, name,
                 doc = "<no help available>",  
                 data_fn = None,  
                 visible = True, 
                 width = MEDIUM_COL_WIDTH,
                 alignment = Qt.AlignLeft):

        if not callable(data_fn):
            raise ValueError("data_fn must be function(TreeItem)->string")
            
        self.name = name
        self.doc = doc
        self.data_fn = data_fn
        self.visible = visible
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
    return hasattr(tree_item.obj, "__call__")    


#######################
# Column definitions ##
#######################

ATTR_COLUMN_PATH = AttributeColumn('Path', 
        doc       = "A path to the data: e.g. var[1]['a'].item", 
        data_fn   = lambda(tree_item): tree_item.obj_path if tree_item.obj_path else '<root>', 
        visible   = True,  
        width     = MEDIUM_COL_WIDTH, 
        alignment = Qt.AlignLeft) 

ATTR_COLUMN_NAME = AttributeColumn('Name', 
        doc       = "The name of the object.", 
        data_fn   = lambda(tree_item): tree_item.obj_name if tree_item.obj_name else '<root>',
        visible   = True,  
        width     = MEDIUM_COL_WIDTH, 
        alignment = Qt.AlignLeft) 

ATTR_COLUMN_VALUE = AttributeColumn('Value', 
        doc       = "The value of the object for atomic objects (int, str, etc)", 
        data_fn   = tio_simple_value,
        visible   = True,  
        width     = MEDIUM_COL_WIDTH, 
        alignment = Qt.AlignLeft) 

ATTR_COLUMN_TYPE = AttributeColumn('Type', 
        doc       = "Type of the object determined using the builtin type() function", 
        data_fn   = lambda(tree_item): str(type(tree_item.obj)),
        visible   = False,  
        width     = MEDIUM_COL_WIDTH, 
        alignment = Qt.AlignLeft) 

ATTR_COLUMN_CLASS = AttributeColumn('Type Name', 
        doc       = "The name of the class of the object via obj.__class__.__name__", 
        data_fn   = lambda(tree_item): type(tree_item.obj).__name__,
        visible   = True,  
        width     = MEDIUM_COL_WIDTH, 
        alignment = Qt.AlignLeft) 

ATTR_COLUMN_CALLABLE = AttributeColumn('Callable', 
        doc       = "The if the is callable (e.g. a function or a method)", 
        data_fn   = tio_is_callable, 
        visible   = True,  
        width     = SMALL_COL_WIDTH,
        alignment = Qt.AlignLeft) 

ATTR_COLUMN_LENGTH = AttributeColumn('Length', 
        doc       = "The length of the object using the len() function", 
        data_fn   = tio_length, 
        visible   = False,  
        width     = SMALL_COL_WIDTH,
        alignment = Qt.AlignLeft) 

ATTR_COLUMN_ID = AttributeColumn('Id', 
        doc       = "The identifier of the object with calculated using the id() function", 
        data_fn   = lambda(tree_item): "0x{:X}".format(id(tree_item.obj)), 
        visible   = False,  
        width     = SMALL_COL_WIDTH,
        alignment = Qt.AlignRight) 

ATTR_COLUMN_PRED = AttributeColumn('Predicates', 
        doc       = "Predicates from the inspect module" ,
        data_fn   = tio_predicates, 
        visible   = False,  
        width     = MEDIUM_COL_WIDTH, 
        alignment = Qt.AlignLeft) 


ALL_ATTR_COLUMNS = (ATTR_COLUMN_PATH, 
                    ATTR_COLUMN_NAME,
                    ATTR_COLUMN_VALUE,
                    ATTR_COLUMN_TYPE, 
                    ATTR_COLUMN_CLASS, 
                    ATTR_COLUMN_CALLABLE, 
                    ATTR_COLUMN_LENGTH, 
                    ATTR_COLUMN_ID, 
                    ATTR_COLUMN_PRED)

DEFAULT_ATTR_COLUMNS = ALL_ATTR_COLUMNS
