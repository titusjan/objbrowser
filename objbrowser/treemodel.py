""" Module that defines the TreeModel
"""
# Based on: PySide examples/itemviews/simpletreemodel
# See: http://harmattan-dev.nokia.com/docs/library/html/qt4/itemviews-simpletreemodel.html

from __future__ import absolute_import
import logging, types, inspect
from PySide import QtCore, QtGui
from PySide.QtCore import Qt
from objbrowser.treeitem import TreeItem

logger = logging.getLogger(__name__)

def is_special_method(method_name):
    "Returns true if the method name starts and ends with two underscores"
    return method_name.startswith('__') and method_name.endswith('__') 


def predicates(obj):
    """ Returns the inspect module predicates that are true for this object
    """
    all_pred = (inspect.ismodule, inspect.isclass, inspect.ismethod, 
                inspect.isfunction, inspect.isgeneratorfunction, inspect.isgenerator,
                inspect.istraceback, inspect.isframe, inspect.iscode, 
                inspect.isbuiltin, inspect.isroutine, inspect.isabstract, 
                inspect.ismethoddescriptor, inspect.isdatadescriptor, inspect.isgetsetdescriptor,
                inspect.ismemberdescriptor)  
    has_predicates = [pred.__name__ for pred in all_pred if pred(obj)]
    return ", ".join(has_predicates)


def simple_value(obj):
    """ Returns a the string representation of obj if it has a 'simple' type.
        
        That is: the type is a scalar or a string, not a compound such as a list.
    """
    obj_type = type(obj)
    if obj_type in (types.BooleanType, types.FloatType, types.IntType, types.NoneType):
        return repr(obj)
    elif obj_type == types.StringType:
        return repr(obj.encode('string_escape'))
    elif obj_type == types.UnicodeType:
        return repr(obj.encode('unicode_escape'))
    else:
        return ""
    
# Keep the method names camelCase since it inherits from a Qt object.
# Disabled need for docstrings. For a good explanation of the methods, take a look
# at the Qt simple tree model example.
# See: http://harmattan-dev.nokia.com/docs/library/html/qt4/itemviews-simpletreemodel.html
# pylint: disable=C0103, C0111

# The main window inherits from a Qt class, therefore it has many 
# ancestors public methods and attributes.
# pylint: disable=R0901, R0902, R0904, W0201 
    
class TreeModel(QtCore.QAbstractItemModel):
    """ Model that provides an interface to an objectree that is build of TreeItems. 
    """
    
    # Tree column indices
    COL_PATH      = 0   # A path to the data: e.g. var[1]['a'].item
    COL_NAME      = 1   # The name of the node. 
    COL_VALUE     = 2   # The value of the node for atomic nodes (int, str, etc)
    COL_TYPE      = 3   # Type of the node determined using the builtin type() function
    COL_CLASS     = 4   # The name of the class of the node via node.__class__.__name__
    COL_ID        = 5   # The identifier of the object with calculated using the id() function
    COL_PREDICATE = 6   # Predicates from the inspect module
    
    N_COLS = 7
    HEADERS = [None] * N_COLS 
    HEADERS[COL_PATH]      = 'Path'
    HEADERS[COL_NAME]      = 'Name'
    HEADERS[COL_VALUE]     = 'Value'
    HEADERS[COL_TYPE]      = 'Type'
    HEADERS[COL_CLASS]     = 'Type Name'
    HEADERS[COL_ID]        = 'Id'
    HEADERS[COL_PREDICATE] = 'Predicates'
    
    def __init__(self, obj, obj_name = '', 
                 show_special_methods = True, 
                 single_root_node=False, 
                 parent=None):
        """ Constructor
        
            :param obj: any Python object or variable
            :param obj_name: name of the object as it will appear in the root node
            :param show_special_methods: if True the objects special methods, 
                i.e. methods with a name that starts and ends with two underscores, 
                will be displayed (in grey). If False they are hidden.
            :param single_root_node: If true, all items are grouped under a single root item
            :param parent: the parent widget
        """
        super(TreeModel, self).__init__(parent)
        self._root_obj  = obj
        self._root_name = obj_name 
        self._single_root_node = single_root_node
        self._show_special_methods = show_special_methods
        self.root_item = self.populateTree(obj, obj_name, single_root_node)


    def columnCount(self, _parent):
        """ Returns the number of columns in the tree """
        return self.N_COLS


    def data(self, index, role):
        """ Returns the tree item at the given index and role
        """
        if not index.isValid():
            return None

        col = index.column()
        tree_item = index.internalPointer()
        obj = tree_item.obj

        if role == Qt.DisplayRole:
            
            if col == self.COL_PATH:
                return tree_item.obj_path if tree_item.obj_path else '<root>'
            elif col == self.COL_NAME:
                return tree_item.obj_name if tree_item.obj_name else '<root>'
            elif col == self.COL_TYPE:
                return str(type(obj))
            elif col == self.COL_CLASS:
                return type(obj).__name__
            elif col == self.COL_VALUE:
                return simple_value(obj)
            elif col == self.COL_ID:
                return "0x{:X}".format(id(obj))
            elif col == self.COL_PREDICATE:
                return predicates(obj)
            else:
                raise ValueError("Unexpected column: {}".format(col))
            
        elif role == Qt.TextAlignmentRole:
            if col == self.COL_ID:
                return Qt.AlignRight
            else:
                return Qt.AlignLeft
            
        elif role == Qt.ForegroundRole:
            
            if is_special_method(tree_item.obj_name): 
                return QtGui.QBrush(QtGui.QColor('grey'))
            else:
                return QtGui.QBrush(QtGui.QColor('black'))
        else:
            return None


    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable


    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.HEADERS[section]
        else:
            return None

    def treeItem(self, index):
        if not index.isValid():
            return self.root_item
        else:
            return index.internalPointer() 
            

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        parentItem = self.treeItem(parent)
        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()


    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        child_item = index.internalPointer()
        parent_item = child_item.parent()

        if parent_item == self.root_item:
            return QtCore.QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)


    def rowCount(self, parent):
        
        if parent.column() > 0:
            return 0
        else:
            return self.treeItem(parent).child_count()


    def hasChildren(self, parent):
        if parent.column() > 0:
            return 0
        else:
            return self.treeItem(parent).has_children
    

    def canFetchMore(self, parent):
        if parent.column() > 0:
            return 0
        else:
            result = not self.treeItem(parent).children_fetched 
            #logger.debug("canFetchMore: {} = {}".format(parent, result))
            return result  


    def fetchMore(self, parent):

        if parent.column() > 0:
            return
        
        parent_item = self.treeItem(parent)
        if parent_item.children_fetched:
            return
        
        logger.debug("fetchMore: {}".format(parent))
        
        obj = parent_item.obj
        obj_path = parent_item.obj_path
        
        if isinstance(obj, (list, tuple)):
            obj_items = sorted(enumerate(obj))
            path_strings = ['{}[{}]'.format(obj_path, item[0]) if obj_path else item[0] 
                            for item in obj_items]
        elif isinstance(obj, (set, frozenset)):
            obj_items = [('pop()', elem) for elem in sorted(obj)]
            path_strings = ['{0}.pop()'.format(obj_path, item[0]) if obj_path else item[0] 
                            for item in obj_items]
        elif isinstance(obj, dict):
            obj_items = sorted(obj.iteritems())
            path_strings = ['{}[{!r}]'.format(obj_path, item[0]) if obj_path else item[0] 
                            for item in obj_items]
        else:
            obj_items = []
            path_strings = []
        
        # Since every variable is an object we also add its members to the tree.
        obj_members = sorted(inspect.getmembers(obj))
        if self._show_special_methods is False:
            obj_members = [memb for memb in obj_members if not is_special_method(memb[0])]
        obj_items.extend(obj_members)
        path_strings.extend(['{}.{}'.format(obj_path, memb[0]) if obj_path else memb[0] 
                             for memb in obj_members])
        
        assert len(obj_items) == len(path_strings), "sanity check"
        self.beginInsertRows(parent, 0, len(obj_items))
        for item, path_str in zip(obj_items, path_strings):
            name, child_obj = item
            parent_item.append_child(self._addTreeItem(parent_item, child_obj, name, path_str))
        parent_item.children_fetched = True                
        self.endInsertRows()                       
        

    
    def _addTreeItem(self, parent_item, obj, obj_name, obj_path):
        """ Helper function that recursively adds nodes.

            :param parent_item: The parent 
            :param obj: The object that will be added to the tree.
            :param obj_name: Labels how this node is known to the parent
            :param obj_path: full path to this node, e.g.: var[idx1]['key'].item
            
            Returns newly created tree item
        """
        #logger.debug("Inserting: {} = {!r}".format(obj_name, obj))
        tree_item = TreeItem(parent_item, obj, obj_name, obj_path)
        return tree_item

   
    def populateTree(self, root_obj, root_name='', single_root_node=False):
        """ Fills the tree using a python object.
        """
        logger.debug("populateTree with object id = 0x{:x}".format(id(root_obj)))
        
        if single_root_node is True:
            root_parent_item = TreeItem(None, None, '<root_parent>', '<root_parent>') 
            root_parent_item.children_fetched = True
            root_item = self._addTreeItem(root_parent_item, root_obj, root_name, root_name)
            root_parent_item.append_child(root_item)
            return root_parent_item
        else:
            return self._addTreeItem(None, root_obj, root_name, root_name)
            
        
    def setShowSpecialMethods(self, show_special_methods):
        """ Shows/hides special methods, which begin with an underscore.
            Repopulates the tree.
        """
        logger.debug("setShowSpecialMethods: {}".format(show_special_methods))
        self._show_special_methods = show_special_methods
        self.beginResetModel()
        self.reset()
        self.root_item = self.populateTree(self._root_obj, self._root_name, 
                                           self._single_root_node)
        self.endResetModel()
        

        