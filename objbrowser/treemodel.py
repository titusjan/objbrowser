""" Module that defines the TreeModel
"""
# Based on: PySide examples/itemviews/simpletreemodel
# See: https://github.com/PySide/Examples/blob/master/examples/itemviews/simpletreemodel/simpletreemodel.py

# TODO: a lot of methods (e.g. rowCount) test if parent.column() > 0. This should probably 
# be replaced with an assert.


from __future__ import absolute_import
import logging, inspect
from difflib import SequenceMatcher
from collections import OrderedDict
from six import unichr

from qtpy import QtCore, QtGui, QtWidgets
from qtpy.QtCore import Qt
from objbrowser.treeitem import TreeItem
from objbrowser.utils import cut_off_str

logger = logging.getLogger(__name__)



    
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
    def __init__(self, obj, 
                 obj_name = '',
                 attr_cols = None, 
                 parent = None):
        """ Constructor
        
            :param obj: any Python object or variable
            :param obj_name: name of the object as it will appear in the root node
                             If empty, no root node will be drawn. 
            :param attr_cols: list of AttributeColumn definitions
            :param parent: the parent widget
        """
        super(TreeModel, self).__init__(parent)
        self._attr_cols = attr_cols

        self.regular_font = QtGui.QFont()  # Font for members (non-functions)
        self.dunder_attribute_font = QtGui.QFont()  # Font for __dunder_attributes__
        self.dunder_attribute_font.setItalic(True)
        
        self.regular_color = QtGui.QBrush(QtGui.QColor('black'))    
        #self.callable_color = QtGui.QBrush(QtGui.QColor('brown'))  # for functions, methods, etc.
        self.callable_color = QtGui.QBrush(QtGui.QColor('mediumblue'))  # for functions, methods, etc.

        # The following members will be initialized by populateTree
        # The rootItem is always invisible. If the obj_name is the empty string, the inspectedItem 
        # will be the rootItem (and therefore be invisible). If the obj_name is given, an 
        # invisible root item will be added and the inspectedItem will be its only child. 
        # In that case the inspected item will be visible. 
        self._inspected_node_is_visible = None 
        self._inspected_item = None
        self._root_item = None
        self.populateTree(obj, obj_name)

    
    @property
    def inspectedNodeIsVisible(self):
        """ Returns True if the inspected node is visible. 
            In that case an invisible root node has been added.
        """
        return self._inspected_node_is_visible
    
    
    @property
    def rootItem(self):
        """ The root TreeItem.
        """
        return self._root_item
    
    
    @property
    def inspectedItem(self): # TODO: needed?
        """ The TreeItem that contains the item under inspection.
        """
        return self._inspected_item
    

    def rootIndex(self): # TODO: needed?
        """ The index that returns the root element (same as an invalid index).
        """
        return QtCore.QModelIndex()

    
    def inspectedIndex(self):
        """ The model index that point to the inspectedItem
        """
        if self.inspectedNodeIsVisible:
            return self.createIndex(0, 0, self._inspected_item)
        else:
            return self.rootIndex()
        

    def columnCount(self, _parent=None):
        """ Returns the number of columns in the tree """
        return len(self._attr_cols)


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
            if tree_item.is_callable:
                return self.callable_color
            else:
                return self.regular_color
            
        elif role == Qt.FontRole:
            if tree_item.is_attribute:
                return self.dunder_attribute_font
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
            return self.rootItem
        else:
            return index.internalPointer() 
            

    def index(self, row, column, parent=None):
        
        if parent is None:
            logger.debug("parent is None")
            parent = QtCore.QModelIndex()

        parentItem = self.treeItem(parent)
            
        if not self.hasIndex(row, column, parent):
            logger.debug("hasIndex is False: ({}, {}) {!r}".format(row, column, parentItem))
            #logger.warn("Parent index model: {!r} != {!r}".format(parent.model(), self))

            return QtCore.QModelIndex()

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

        if parent_item is None or parent_item == self.rootItem:
            return QtCore.QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)
    

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
        
        self.beginInsertRows(parent, 0, len(tree_items) - 1)
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
                obj_children = list(obj.items())
            except Exception as ex:
                # Can happen if the items method expects an argument, for instance the  
                # types.DictType.items method expects a dictionary.
                logger.warn("No items expanded. Objects items() call failed: {}".format(ex))
                obj_children = []

            # Sort keys, except when the object is an OrderedDict.
            if not isinstance(obj, OrderedDict):
                try:
                    obj_children = sorted(obj.items())
                except Exception as ex:
                    logger.debug("Unable to sort dictionary keys: {}".format(ex))
                    
            path_strings = ['{}[{!r}]'.format(obj_path, item[0]) if obj_path else item[0] 
                            for item in obj_children]
        
        assert len(obj_children) == len(path_strings), "sanity check"    
        is_attr_list = [False] * len(obj_children)
        
        # Object attributes
        for attr_name, attr_value in sorted(inspect.getmembers(obj)):
            obj_children.append( (attr_name, attr_value) )
            path_strings.append('{}.{}'.format(obj_path, attr_name) if obj_path else attr_name)
            is_attr_list.append(True)

        assert len(obj_children) == len(path_strings), "sanity check"
        tree_items = []
        for item, path_str, is_attr in zip(obj_children, path_strings, is_attr_list):
            name, child_obj = item
            tree_items.append(TreeItem(child_obj, name, path_str, is_attr))
            
        return tree_items

   
    def populateTree(self, obj, obj_name='', inspected_node_is_visible=None):
        """ Fills the tree using a python object. Sets the rootItem.
        """
        logger.debug("populateTree with object id = 0x{:x}".format(id(obj)))
        
        if inspected_node_is_visible is None:
            inspected_node_is_visible = (obj_name != '')
        self._inspected_node_is_visible = inspected_node_is_visible
        
        if self._inspected_node_is_visible:
            self._root_item = TreeItem(None, '<invisible_root>', '<invisible_root>', None) 
            self._root_item.children_fetched = True
            self._inspected_item = TreeItem(obj, obj_name, obj_name, is_attribute = None)
            self._root_item.append_child(self._inspected_item)
        else:
            # The root itself will be invisible
            self._root_item = TreeItem(obj, obj_name, obj_name, is_attribute = None)
            self._inspected_item = self._root_item
            
            # Fetch all items of the root so we can select the first row in the constructor.
            root_index = self.index(0, 0)
            self.fetchMore(root_index) 
            
                
                
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
        logger.info("refreshTree: {}".format(self.rootItem))
        
        root_item = self.treeItem(self.rootIndex())
        logger.info("  root_item:      {} (idx={})".format(root_item, self.rootIndex()))
        inspected_item = self.treeItem(self.inspectedIndex())
        logger.info("  inspected_item: {} (idx={})".format(inspected_item, self.inspectedIndex()))
        
        assert (root_item is inspected_item) != self.inspectedNodeIsVisible, "sanity check"
        
        self._auxRefreshTree(self.inspectedIndex())
        
        root_obj = self.rootItem.obj
        logger.debug("After _auxRefreshTree, root_obj: {}".format(cut_off_str(root_obj, 80)))
        self.rootItem.pretty_print()
        
        # Emit the dataChanged signal for all cells. This is faster than checking which nodes
        # have changed, which may be slow for some underlying Python objects.
        n_rows = self.rowCount()
        n_cols = self.columnCount()
        top_left = self.index(0, 0)
        bottom_right = self.index(n_rows-1, n_cols-1)
        
        logger.debug("bottom_right: ({}, {})".format(bottom_right.row(), bottom_right.column()))
        self.dataChanged.emit(top_left, bottom_right)
        


# TODO: look at QSortFilterProxyModel.﻿dynamicSortFilter, (implement hasChildren?)
# ﻿Since QAbstractProxyModel and its subclasses are derived from QAbstractItemModel, much of the
# same advice about subclassing normal models also applies to proxy models. In addition, it is
# worth noting that many of the default implementations of functions in this class are written so
# that they call the equivalent functions in the relevant source model. This simple proxying
# mechanism may need to be overridden for source models with more complex behavior; for example,
# if the source model provides a custom hasChildren() implementation, you should also provide one
# in the proxy model.
# Note: Some general guidelines for subclassing models are available in the Model Subclassing Reference.



class TreeProxyModel(QtCore.QSortFilterProxyModel):
    """ Proxy model that overrides the sorting and can filter out items
    """
    def __init__(self,
                 show_callable_attributes = True,
                 show_dunder_attributes = True,
                 parent = None):
        """ Constructor
        
            :param show_callable_attributes: if True the callables objects,
                i.e. objects (such as function) that  a __call__ method, 
                will be displayed (in brown). If False they are hidden.
            :param show_dunder_attributes: if True the objects dunder attributes,
                i.e. methods with a name that starts and ends with two underscores, 
                will be displayed (in italics). If False they are hidden.
            :param parent: the parent widget
        """
        super(TreeProxyModel, self).__init__(parent)

        self._show_callables = show_callable_attributes
        self._show_dunder_attributes = show_dunder_attributes


    def treeItem(self, proxy_index):
        index = self.mapToSource(proxy_index)
        return self.sourceModel().treeItem(index)
    
    
    def firstItemIndex(self): 
        """ Returns the first child of the root item.
        """
        # We cannot just call the same function of the source model because the first node
        # there may be hidden.
        source_root_index = self.sourceModel().rootIndex()
        proxy_root_index = self.mapFromSource(source_root_index)
        first_item_index = self.index(0, 0, proxy_root_index)
        return first_item_index
            

    def filterAcceptsRow(self, sourceRow, sourceParentIndex):
        """ Returns true if the item in the row indicated by the given source_row and 
            source_parent should be included in the model.
        """
        parent_item = self.sourceModel().treeItem(sourceParentIndex)
        tree_item = parent_item.child(sourceRow)
        
        accept = ((self._show_dunder_attributes or not tree_item.is_dunder_attribute) and
                  (self._show_callables or not tree_item.is_callable_attribute))

        #logger.debug("filterAcceptsRow = {}: {}".format(accept, tree_item))
        return accept
    
    
    def getShowCallables(self):
        return self._show_callables

        
    def setShowCallables(self, show_callables):
        """ Shows/hides show_callables, which have a __call__ attribute.
            Repopulates the tree.
        """
        logger.debug("setShowCallables: {}".format(show_callables))
        self._show_callables = show_callables
        self.invalidateFilter()


    def getShowDunderAttributes(self):
        return self._show_dunder_attributes
        
        
    def setShowDunderAttributes(self, show_dunder_attributes):
        """ Shows/hides dunder attributes, which begin with an underscore.
            Repopulates the tree.
        """
        logger.debug("setShowDunderAttributes: {}".format(show_dunder_attributes))
        self._show_dunder_attributes = show_dunder_attributes
        self.invalidateFilter()
        
