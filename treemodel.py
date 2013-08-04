
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

        self._populate_tree(obj)


    def columnCount(self, parent):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self.rootItem.columnCount()


    def data(self, index, role):
        if not index.isValid():
            return None

        if role != QtCore.Qt.DisplayRole:
            return None

        item = index.internalPointer()

        return item.data(index.column())


    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.NoItemFlags

        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable


    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.HEADERS[section]
        else:
            return None


    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QtCore.QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

   
    def _populate_tree(self, root_obj, root_name=None, single_root_node=False):
        """ Fills the tree using a python object.
        """
        logger.debug("_populate_tree with object id = 0x{:x}".format(id(root_obj)))
        
        def add_node(parent_item, obj, obj_name, obj_path):
            """ Helper function that recursively adds nodes.

                :param parent_item: The parent 
                :param obj: The object that will be added to the tree.
                :param obj_name: Labels how this node is known to the parent
                :param obj_path: full path to this node, e.g.: var[idx1]['key'].item
                
                Returns newly created tree item
            """

            logger.debug("Inserting: {} = {!r}".format(obj_name, obj))
            tree_item = TreeItem(self.N_COLS, parent_item)
            
            # TODO: sets and objects
            tree_item.set_data(self.COL_PATH,  str(obj_path) if obj_path is not None else '<root>')
            tree_item.set_data(self.COL_NAME,  str(obj_name) if obj_name is not None else '<root>')
            tree_item.set_data(self.COL_TYPE,  str(type(obj)))
            tree_item.set_data(self.COL_CLASS, class_name(obj))
            tree_item.set_data(self.COL_VALUE, simple_value(obj))
            tree_item.set_data(self.COL_STR,   str(obj))
            tree_item.set_data(self.COL_REPR,  repr(obj))
            
            obj_type = type(obj)
            if obj_type == types.ListType or obj_type == types.TupleType:
                for idx, value in enumerate(obj):
                    tree_item.appendChild(add_node(tree_item, value, idx, 
                                                   '{}[{}]'.format(obj_path, idx)))
                    
            elif obj_type == types.DictionaryType:
                for key, value in sorted(obj.iteritems()):
                    path_str = '{}[{!r}]'.format(obj_path, key) if obj_path else key
                    tree_item.appendChild(add_node(tree_item, value, key, path_str)) 
            
            #else:
            #    for name, value in inspect.getmembers(obj):
            #        add_node(tree_item, value, name, 
            #                 '{}[{!r}]'.format(obj_path, name) if obj_path else name)
            return tree_item
                                
        # End helper function.
        
        if single_root_node is True:
            root_parent_item = TreeItem(self.N_COLS, None) # Will never be accessed by the view
            root_item = add_node(root_parent_item, root_obj, root_name, root_name)
            root_parent_item.appendChild(root_item)
            self.rootItem = root_parent_item
        else:
            self.rootItem = add_node(None, root_obj, root_name, root_name)
            
        
        