
############################################################################
##
## Copyright (C) 2005-2005 Trolltech AS. All rights reserved.
##
## This file is part of the example classes of the Qt Toolkit.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following information to ensure GNU
## General Public Licensing requirements will be met:
## http://www.trolltech.com/products/qt/opensource.html
##
## If you are unsure which license is appropriate for your use, please
## review the following information:
## http://www.trolltech.com/products/qt/licensing.html or contact the
## sales department at sales@trolltech.com.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################

# Based on: PySide examples/itemviews/simpletreemodel
# See: http://harmattan-dev.nokia.com/docs/library/html/qt4/itemviews-simpletreemodel.html

import logging, types, inspect
from PySide import QtCore
from treeitem import TreeItem

logger = logging.getLogger(__name__)


        
def class_name(obj):
    """ Returns the name of the class of the object.
        Returns empty string if it cannot be determined, 
        e.g. in old-style classes.
    """
    try:
        return obj.__class__.__name__
    except AttributeError:
        return ''

        
def simple_value(obj):
    """ Returns a the string representation of obj if it has a 'simple' type.
        
        That is: the type is a scalar or a string, not a compound such as a list.
    """
    if type(obj) in (types.BooleanType, types.FloatType, types.IntType, types.NoneType, 
                     types.StringType, types.UnicodeType):
        return repr(obj)
    else:
        return ""
    
    
class TreeModel(QtCore.QAbstractItemModel):
    
    # Tree column indices
    COL_PATH  = 0   # A path to the data: e.g. var[1]['a'].item
    COL_NAME  = 1   # The name of the node. 
    COL_VALUE = 2   # The value of the node for atomic nodes (int, str, etc)
    COL_TYPE  = 3   # Type of the node determined using the builtin type() function
    COL_CLASS = 4   # The name of the class of the node via node.__class__.__name__
    COL_STR   = 5   # The string conversion of the node using __str__()
    COL_REPR  = 6   # The string conversion of the node using __repr__()
    N_COLS = 7
    
    HEADERS = [None] * N_COLS 
    HEADERS[COL_PATH]  = 'Path'
    HEADERS[COL_NAME]  = 'Name'
    HEADERS[COL_VALUE] = 'Value'
    HEADERS[COL_TYPE]  = 'Type'
    HEADERS[COL_CLASS] = 'Class'
    HEADERS[COL_STR]   = 'Str'
    HEADERS[COL_REPR]  = 'Repr'
    
    def __init__(self, obj, parent=None):
        super(TreeModel, self).__init__(parent)
        self.root_item = self._populateTree(obj)


    def columnCount(self, parent):
        return self.N_COLS


    def data(self, index, role):
        if not index.isValid():
            return None

        if role != QtCore.Qt.DisplayRole:
            return None

        tree_item = index.internalPointer()
        obj = tree_item.obj
        col = index.column()
        
        if col == self.COL_PATH:
            return tree_item.obj_path if tree_item.obj_path is not None else '<root>'
        if col == self.COL_NAME:
            return tree_item.obj_name if tree_item.obj_name is not None else '<root>'
        if col == self.COL_TYPE:
            return str(type(obj))
        if col == self.COL_CLASS:
            return class_name(obj)
        if col == self.COL_VALUE:
            return simple_value(obj)
        if col == self.COL_STR:
            return str(obj)
        if col == self.COL_REPR:
            return repr(obj)
        

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.NoItemFlags

        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable


    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.HEADERS[section]
        else:
            return None

    def _tree_item(self, index):
        if not index.isValid():
            return self.root_item
        else:
            return index.internalPointer() 
            

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        parentItem = self._tree_item(parent)
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
            return self._tree_item(parent).child_count()


    def hasChildren(self, parent):
        if parent.column() > 0:
            return 0
        else:
            return self._tree_item(parent).has_children
    

    def canFetchMore(self, parent):
        if parent.column() > 0:
            return 0
        else:
            result = not self._tree_item(parent).children_fetched 
            #logger.debug("canFetchMore: {} = {}".format(parent, result))
            return result  


    def fetchMore(self, parent):

        if parent.column() > 0:
            return
        
        parent_item = self._tree_item(parent)
        if parent_item.children_fetched:
            return
        
        logger.debug("fetchMore: {}".format(parent))
        
        obj = parent_item.obj
        obj_type = type(obj)
        obj_path = parent_item.obj_path
        
        if obj_type == types.ListType or obj_type == types.TupleType:
            self.beginInsertRows(parent, 0, len(obj))

            for idx, value in enumerate(obj):
                parent_item.append_child(self._addTreeItem(parent_item, value, idx, 
                                                          '{}[{}]'.format(obj_path, idx)))
            parent_item.children_fetched = True
            self.endInsertRows()   
        elif obj_type == types.DictionaryType:
            self.beginInsertRows(parent, 0, len(obj))
            for key, value in sorted(obj.iteritems()):
                path_str = '{}[{!r}]'.format(obj_path, key) if obj_path else key
                parent_item.append_child(self._addTreeItem(parent_item, value, key, path_str))
            parent_item.children_fetched = True                
            self.endInsertRows()
        else:
            logger.warn("Unexpected object type: {} {}".format(parent_item, obj_type))
            parent_item.children_fetched = True
            #raise ValueError("Unexpected object type: {}".format(obj_type)) 
            
            # TODO: sets and objects
            #else:
            #    for name, value in inspect.getmembers(obj):
            #        _addTreeItem(tree_item, value, name, 
            #                 '{}[{!r}]'.format(obj_path, name) if obj_path else name)
                                
        

    
    def _addTreeItem(self, parent_item, obj, obj_name, obj_path):
        """ Helper function that recursively adds nodes.

            :param parent_item: The parent 
            :param obj: The object that will be added to the tree.
            :param obj_name: Labels how this node is known to the parent
            :param obj_path: full path to this node, e.g.: var[idx1]['key'].item
            
            Returns newly created tree item
        """
        logger.debug("Inserting: {} = {!r}".format(obj_name, obj))
        tree_item = TreeItem(parent_item, obj, obj_name, obj_path)

        expandable_types = (types.TupleType, types.ListType, types.DictionaryType)
        tree_item.has_children = (type(obj) in expandable_types)
        tree_item.children_fetched 
        return tree_item

   
    def _populateTree(self, root_obj, root_name=None, single_root_node=True):
        """ Fills the tree using a python object.
        """
        logger.debug("_populateTree with object id = 0x{:x}".format(id(root_obj)))
        
        if single_root_node is True:
            root_parent_item = TreeItem(None, None, '<root_parent>', '<root_parent>') 
            root_parent_item.children_fetched = True
            root_item = self._addTreeItem(root_parent_item, root_obj, root_name, root_name)
            root_parent_item.append_child(root_item)
            return root_parent_item
        else:
            return self._addTreeItem(None, root_obj, root_name, root_name)
            
        
        