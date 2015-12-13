""" Module that defines the TreeModel
"""
# Based on: PySide examples/itemviews/simpletreemodel
# See: https://github.com/PySide/Examples/blob/master/examples/itemviews/simpletreemodel/simpletreemodel.py

# TODO: a lot of methods (e.g. rowCount) test if parent.column() > 0. This should probably 
# be replaced with an assert.


from __future__ import absolute_import
import logging, inspect
from difflib import SequenceMatcher
from six import unichr

from objbrowser.qtimp import QtCore, QtGui#, Qt
from objbrowser.qtimp.QtCore import Qt
from objbrowser.treeitem import TreeItem

logger = logging.getLogger(__name__)


def is_special_attribute(method_name):
    "Returns true if the method name starts and ends with two underscores"
    return method_name.startswith('__') and method_name.endswith('__') 


    
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
    def __init__(self, root_obj, 
                 root_obj_name = '',
                 attr_cols = None, 
                 show_routine_attributes = True,
                 show_special_attributes = True,
                 parent = None):
        """ Constructor
        
            :param obj: any Python object or variable
            :param name: name of the object as it will appear in the root node
                             If empty, no root node drawn. 
            :param attr_cols: list of AttributeColumn definitions
            :param show_routine_attributes: if True the callables objects, 
                i.e. objects (such as function) that  a __call__ method, 
                will be displayed (in brown). If False they are hidden.
            :param show_special_attributes: if True the objects special attributes, 
                i.e. methods with a name that starts and ends with two underscores, 
                will be displayed (in italics). If False they are hidden.
            :param parent: the parent widget
        """
        super(TreeModel, self).__init__(parent)
        
        self._root_obj = root_obj
        self._root_name = root_obj_name 
        self._attr_cols = attr_cols
        self._show_callables = show_routine_attributes
        self._show_special_attributes = show_special_attributes
        self.root_item = self.populateTree(root_obj, root_obj_name, )
        
        self.regular_font = QtGui.QFont()  # Font for members (non-functions)
        self.special_attribute_font = QtGui.QFont()  # Font for __special_attributes__
        self.special_attribute_font.setItalic(True)
        
        self.regular_color = QtGui.QBrush(QtGui.QColor('black'))    
        #self.routine_color = QtGui.QBrush(QtGui.QColor('brown'))  # for functions, methods, etc.
        self.routine_color = QtGui.QBrush(QtGui.QColor('mediumblue'))  # for functions, methods, etc.


    def columnCount(self, _parent=None):
        """ Returns the number of columns in the tree """
        return len(self._attr_cols)
    
    @property
    def show_root_node(self):
        """ If True, a root node is present"""
        return (self._root_name != '')

    def data(self, index, role):
        """ Returns the tree item at the given index and role
        """
        if not index.isValid():
            return None

        col = index.column()
        tree_item = index.internalPointer()
        obj = tree_item.obj

        if role == Qt.DisplayRole:
            try:
                attr = self._attr_cols[col].data_fn(tree_item)
                # Replace carriage returns and line feeds with unicode glyphs 
                # so that all table rows fit on one line. 
                #return attr.replace('\n', unichr(0x240A)).replace('\r', unichr(0x240D))
                return (attr.replace('\r\n', unichr(0x21B5))
                            .replace('\n', unichr(0x21B5))
                            .replace('\r', unichr(0x21B5)))
            except Exception as ex:
                #logger.exception(ex)
                return "**ERROR**: {}".format(ex) 
            
        elif role == Qt.TextAlignmentRole:
            return self._attr_cols[col].alignment
            
        elif role == Qt.ForegroundRole:
            if inspect.isroutine(obj):
                return self.routine_color
            else:
                return self.regular_color
            
        elif role == Qt.FontRole:
            if is_special_attribute(tree_item.obj_name):
                return self.special_attribute_font
            else:
                return self.regular_font
        else:
            return None


    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable


    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._attr_cols[section].name
        else:
            return None

    def treeItem(self, index):
        if not index.isValid():
            return self.root_item
        else:
            return index.internalPointer() 
            

    def index(self, row, column, parent=None):
        
        if parent is None:
            logger.warn("parent is None")
            parent = QtCore.QModelIndex()
            
        if not self.hasIndex(row, column, parent):
            logger.warn("hasIndex is False")
            return QtCore.QModelIndex()

        parentItem = self.treeItem(parent)
        childItem = parentItem.child(row)
        #logger.debug("  {}".format(childItem.obj_path))
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            logger.warn("no childItem")
            return QtCore.QModelIndex()


    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        child_item = index.internalPointer()
        parent_item = child_item.parent()

        if parent_item is None or parent_item == self.root_item:
            return QtCore.QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)
    
    
    def first_item_index(self):
        """ Returns the root item index or, if the single_root_node property is False, 
            the index(0, 0, root_item)
        """
        if self.show_root_node is True:
            root_parent_index = self.createIndex(0, 0, self.root_item)
            return self.index(0, 0, root_parent_index)
        else:
            root_index = self.createIndex(0, 0, self.root_item)
            first_item_index = self.index(0, 0, root_index)
            return first_item_index
            

    def rowCount(self, parent=None):
        parent = QtCore.QModelIndex() if parent is None else parent
        
        if parent.column() > 0:
            # This is taken from the PyQt simpletreemodel example.
            return 0
        else:
            return self.treeItem(parent).child_count()


    def hasChildren(self, parent=None):
        parent = QtCore.QModelIndex() if parent is None else parent
        if parent.column() > 0:
            return 0
        else:
            return self.treeItem(parent).has_children
    

    def canFetchMore(self, parent=None):
        parent = QtCore.QModelIndex() if parent is None else parent
        if parent.column() > 0:
            return 0
        else:
            result = not self.treeItem(parent).children_fetched 
            # logger.debug("canFetchMore: {} = {}".format(parent, result))
            return result  


    def fetchMore(self, parent=None):
        """ Fetches the children given the model index of a parent node.
            Adds the children to the parent.
        """
        parent = QtCore.QModelIndex() if parent is None else parent
        if parent.column() > 0:
            return
        
        parent_item = self.treeItem(parent)
        if parent_item.children_fetched:
            return
                
        tree_items = self._fetchObjectChildren(parent_item.obj, parent_item.obj_path)
        
        self.beginInsertRows(parent, 0, len(tree_items))
        for tree_item in tree_items:
            parent_item.append_child(tree_item)
            
        parent_item.children_fetched = True                
        self.endInsertRows()
        

    def _fetchObjectChildren(self, obj, obj_path):
        """ Fetches the children of a Python object. 
            Returns: list of TreeItems
        """
        obj_children = []
        path_strings = []
        
        if isinstance(obj, (list, tuple)):
            obj_children = sorted(enumerate(obj))
            path_strings = ['{}[{}]'.format(obj_path, item[0]) if obj_path else item[0] 
                            for item in obj_children]
        elif isinstance(obj, (set, frozenset)):
            obj_children = [('pop()', elem) for elem in sorted(obj)]
            path_strings = ['{0}.pop()'.format(obj_path, item[0]) if obj_path else item[0] 
                            for item in obj_children]
        elif hasattr(obj, 'items'): # dictionaries and the likes. 
            try: 
                obj_children = sorted(obj.items())
            except Exception as ex:
                
                # Can happen if the items method expects an argument, for instance the  
                # types.DictType.items method expects a dictionary.
                logger.info("No items expanded. Objects items() call failed: {}".format(ex))
            else:
                path_strings = ['{}[{!r}]'.format(obj_path, item[0]) if obj_path else item[0] 
                                for item in obj_children]
        
        assert len(obj_children) == len(path_strings), "sanity check"    
        is_attr_list = [False] * len(obj_children)
        
        # Object attributes
        for attr_name, attr_value in sorted(inspect.getmembers(obj)):
            if ((self._show_callables or not callable(attr_value)) and
                (self._show_special_attributes or not is_special_attribute(attr_name))):
                obj_children.append( (attr_name, attr_value) )
                path_strings.append('{}.{}'.format(obj_path, attr_name) if obj_path else attr_name)
                is_attr_list.append(True)

        assert len(obj_children) == len(path_strings), "sanity check"
        tree_items = []
        for item, path_str, is_attr in zip(obj_children, path_strings, is_attr_list):
            name, child_obj = item
            tree_items.append(TreeItem(child_obj, name, path_str, is_attr))
            
        return tree_items

   
    def populateTree(self, root_obj, root_name='', single_root_node=False):
        """ Fills the tree using a python object. Sets the root_item.
        """
        logger.debug("populateTree with object id = 0x{:x}".format(id(root_obj)))
        
        if single_root_node is True:
            root_parent_item = TreeItem(None, '<root_parent>', '<root_parent>', None) 
            root_parent_item.children_fetched = True
            root_item = TreeItem(root_obj, root_name, root_name, is_attribute = None)
            root_parent_item.append_child(root_item)
            self.root_item = root_parent_item
        else:
            self.root_item = TreeItem(root_obj, root_name, root_name, is_attribute = None)
            
            # Fetch all items of the root so we can select the first row in the constructor.
            root_index = self.index(0, 0)
            self.fetchMore(root_index) 
            
        return self.root_item
                
                
    def _auxRefreshTree(self, tree_index):
        """ Auxiliary function for refreshTree that recursively refreshes the tree nodes.
            
            If the underlying Python object has been changed, we don't want to delete the old
            tree model and create a new one from scratch because this loses all information about
            which nodes are fetched and expanded. Instead the old tree model is updated. Using the
            difflib from the standard library it is determined for a parent node which child nodes
            should be added or removed. This is done based on the node names only, not on the node 
            contents (the underlying Python objects). Testing the underlying nodes for equality
            is potentially slow. It is faster to let the refreshNode function emit the dataChanged
            signal for all cells.
        """
        
        if not tree_index.isValid():
            logger.warn("index not valid {}".format(tree_index))
        
        tree_item = self.treeItem(tree_index)
        logger.debug("_auxRefreshTree({}): {}{}".format(tree_index, tree_item.obj_path, 
                                           "*" if tree_item.children_fetched else ""))
        
        if tree_item.children_fetched:
            
            old_items = tree_item.child_items
            new_items = self._fetchObjectChildren(tree_item.obj, tree_item.obj_path)
            
            old_item_names = [(item.obj_name, item.is_attribute) for item in old_items]
            new_item_names = [(item.obj_name, item.is_attribute) for item in new_items]
            seqMatcher = SequenceMatcher(isjunk=None, a=old_item_names, b=new_item_names, 
                                         autojunk=False)
            opcodes = seqMatcher.get_opcodes()
            
            logger.debug("(reversed) opcodes: {}".format(list(reversed(opcodes))))
            
            for tag, i1, i2, j1, j2 in reversed(opcodes):
                
                if 1 or tag != 'equal':
                    logger.debug("  {:7s}, a[{}:{}] ({}), b[{}:{}] ({})"
                                 .format(tag, i1, i2, old_item_names[i1:i2], j1, j2, new_item_names[j1:j2]))
                
                if tag == 'equal':
                    # Only when node names are equal is _auxRefreshTree called recursively.
                    assert i2-i1 == j2-j1, "equal sanity check failed {} != {}".format(i2-i1, j2-j1)
                    for old_row, new_row in zip(range(i1, i2), range(j1, j2)):
                        old_items[old_row].obj = new_items[new_row].obj
                        logger.debug("     old_row {} name is equal to {}. Updated object: {}"
                                     .format(old_row, new_row, old_items[old_row].obj))
                        child_index = self.index(old_row, 0, parent=tree_index)
                        self._auxRefreshTree(child_index) 

                elif tag == 'replace':
                    # Explicitly remove the old item and insert the new. The old item may have
                    # child nodes which indices must be removed by Qt, otherwise it crashes.
                    assert i2-i1 == j2-j1, "replace sanity check failed {} != {}".format(i2-i1, j2-j1)
                    
                    first = i1          # row number of first that will be removed
                    last  = i1 + i2 - 1 # row number of last element after insertion
                    logger.debug("     calling beginRemoveRows({}, {}, {})".format(tree_index, first, last)) 
                    self.beginRemoveRows(tree_index, first, last)
                    del tree_item.child_items[i1:i2] 
                    self.endRemoveRows()                    

                    first = i1               # row number of first element after insertion 
                    last  = i1 + j2 - j1 - 1 # row number of last element after insertion
                    logger.debug("     calling beginInsertRows({}, {}, {})".format(tree_index, first, last)) 
                    self.beginInsertRows(tree_index, first, last)
                    tree_item.insert_children(i1, new_items[j1:j2])
                    self.endInsertRows()
                    
                elif tag == 'delete':
                    assert j1 == j2, "delete sanity check failed. {} != {}".format(j1, j2)
                    first = i1          # row number of first that will be removed
                    last  = i1 + i2 - 1 # row number of last element after insertion
                    logger.debug("     calling beginRemoveRows({}, {}, {})".format(tree_index, first, last)) 
                    self.beginRemoveRows(tree_index, first, last)
                    del tree_item.child_items[i1:i2] 
                    self.endRemoveRows()
                                            
                elif tag == 'insert':
                    assert i1 == i2, "insert sanity check failed. {} != {}".format(i1, i2)
                    first = i1               # row number of first element after insertion 
                    last  = i1 + j2 - j1 - 1 # row number of last element after insertion
                    logger.debug("     calling beginInsertRows({}, {}, {})".format(tree_index, first, last)) 
                    self.beginInsertRows(tree_index, first, last)
                    tree_item.insert_children(i1, new_items[j1:j2])
                    self.endInsertRows()

                else:
                    raise ValueError("Invalid tag: {}".format(tag))
            
        
    def refreshTree(self):
        """ Refreshes the tree model from the underlying root object (which may have been changed).
        """
        logger.info("")
        logger.info("refreshTree: {}".format(self.root_item))

        root_obj = self.root_item.obj
        self._auxRefreshTree(QtCore.QModelIndex())
        
        logger.debug("After _auxRefreshTree, root_obj: {}".format(root_obj))
        self.root_item.pretty_print()
        
        # Emit the dataChanged signal for all cells. This is faster than checking which nodes
        # have changed, which may be slow for some underlying Python objects.
        n_rows = self.rowCount()
        n_cols = self.columnCount()
        top_left = self.index(0, 0)
        bottom_right = self.index(n_rows-1, n_cols-1)
        
        logger.debug("bottom_right: ({}, {})".format(bottom_right.row(), bottom_right.column()))
        self.dataChanged.emit(top_left, bottom_right)
        

    
    def getShowCallables(self):
        return self._show_callables
        
    def setShowCallables(self, show_callables):
        """ Shows/hides show_callables, which have a __call__ attribute.
            Repopulates the tree.
        """
        logger.debug("setShowCallables: {}".format(show_callables))
        self._show_callables = show_callables
        self.refreshTree()
    

    def getShowSpecialAttributes(self):
        return self._show_special_attributes
        
    def setShowSpecialAttributes(self, show_special_attributes):
        """ Shows/hides special attributes, which begin with an underscore.
            Repopulates the tree.
        """
        logger.debug("setShowSpecialAttributes: {}".format(show_special_attributes))
        self._show_special_attributes = show_special_attributes
        self.refreshTree()
        


        
