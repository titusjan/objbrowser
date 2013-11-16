""" Module that defines AttributeColumn
"""
from __future__ import absolute_import

import logging, inspect, types

logger = logging.getLogger(__name__)

DEF_COL_WIDTH = 200

class AttributeColumn(object):
    """ Determines how an object attribute is rendered in a table column
    """ 
    def __init__(self, name,
                 doc = "<no help available>",  
                 data_fn = None,  
                 width = DEF_COL_WIDTH, 
                 visible = True, 
                 to_str_fn = None):

        if type(data_fn) != types.FunctionType:
            raise ValueError("data_fn should be function(TreeItem)->string")
            
        self.name = name
        doc = doc
        self.data_fn = data_fn
        self.visible = visible
        self.width = width

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


#######################
# Column definitions ##
#######################

ATTR_COL_PATH = AttributeColumn('Path', 
        doc     = "A path to the data: e.g. var[1]['a'].item", 
        data_fn = lambda(tree_item): tree_item.obj_path if tree_item.obj_path else '<root>', 
        visible = True,  
        width   = DEF_COL_WIDTH) 

ATTR_COL_NAME = AttributeColumn('Name', 
        doc     = "The name of the node.", 
        data_fn = lambda(tree_item): tree_item.obj_name if tree_item.obj_name else '<root>',
        visible = True,  
        width   = DEF_COL_WIDTH) 

ATTR_COL_VALUE = AttributeColumn('Value', 
        doc     = "The value of the node for atomic nodes (int, str, etc)", 
        data_fn = tio_simple_value,
        visible = True,  
        width   = DEF_COL_WIDTH) 

ATTR_COL_TYPE = AttributeColumn('Type', 
        doc     = "Type of the node determined using the builtin type() function", 
        data_fn = lambda(tree_item): str(type(tree_item.obj)),
        visible = False,  
        width   = DEF_COL_WIDTH) 

ATTR_COL_CLASS = AttributeColumn('Type Name', 
        doc     = "The name of the class of the node via node.__class__.__name__", 
        data_fn = lambda(tree_item): type(tree_item.obj).__name__,
        visible = True,  
        width   = DEF_COL_WIDTH) 

ATTR_COL_LENGTH = AttributeColumn('Length', 
        doc     = "The length of the object via len(node)", 
        data_fn = tio_length, 
        visible = True,  
        width   = 120) 

ATTR_COL_ID = AttributeColumn('Id', 
        doc     = "The identifier of the object with calculated using the id() function", 
        data_fn = lambda(tree_item): "0x{:X}".format(id(tree_item.obj)), 
        visible = False,  
        width   = 120) 

ATTR_COL_PRED = AttributeColumn('Predicates', 
        doc     = "Predicates from the inspect module" ,
        data_fn = tio_predicates, 
        visible = False,  
        width   = DEF_COL_WIDTH) 


DEFAULT_ATTR_COLS = (ATTR_COL_PATH, 
                     ATTR_COL_NAME,
                     ATTR_COL_VALUE,
                     ATTR_COL_TYPE, 
                     ATTR_COL_CLASS, 
                     ATTR_COL_LENGTH, 
                     ATTR_COL_ID, 
                     ATTR_COL_PRED)
