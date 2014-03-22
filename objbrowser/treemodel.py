""" Module that defines the TreeModel
"""
# Based on: PySide examples/itemviews/simpletreemodel
# See: http://harmattan-dev.nokia.com/docs/library/html/qt4/itemviews-simpletreemodel.html

from __future__ import absolute_import
import logging, inspect
from PySide import QtCore, QtGui
from PySide.QtCore import Qt
from objbrowser.treeitem import TreeItem

logger = logging.getLogger(__name__)

def is_callable(obj):
    "Returns is obj is callable"
    return hasattr(obj, "__call__")
    

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
                 show_callables = True,
                 show_special_attributes = True,
                 parent = None):
        """ Constructor
        
            :param obj: any Python object or variable
            :param obj_name: name of the object as it will appear in the root node
                             If empty, no root node drawn. 
            :param attr_cols: list of AttributeColumn definitions
            :param show_callables: if True the callables objects, 
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
        self._show_callables = show_callables
        self._show_special_attributes = show_special_attributes
        self.root_item = self.populateTree(root_obj, root_obj_name, )
        
        self.regular_font = QtGui.QFont()  # Font for members (non-functions)
        self.special_attribute_font = QtGui.QFont()  # Font for __special_attributes__
        self.special_attribute_font.setItalic(True)
        
        self.regular_color = QtGui.QBrush(QtGui.QColor('black'))    
        self.callable_color = QtGui.QBrush(QtGui.QColor('brown'))  # for functions, methods, etc.


    def columnCount(self, _parent):
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
            except StandardError, ex:
                logger.exception(ex)
                return "*ERROR*: {}".format(ex) 
            
        elif role == Qt.TextAlignmentRole:
            return self._attr_cols[col].alignment
            
        elif role == Qt.ForegroundRole:
            if is_callable(obj):
                return self.callable_color
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
            parent = QtCore.QModelIndex()
            
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
            # logger.debug("canFetchMore: {} = {}".format(parent, result))
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
        elif hasattr(obj, 'iteritems'): # dictionaries and the likes
            obj_items = sorted(obj.iteritems())
            path_strings = ['{}[{!r}]'.format(obj_path, item[0]) if obj_path else item[0] 
                            for item in obj_items]
        else:
            obj_items = []
            path_strings = []
        
        # Since every variable is an object we also add its members to the tree.
        obj_members = []
        for memb in sorted(inspect.getmembers(obj)):
            #logger.debug("inspect.getmembers(obj): {} ({})".format(memb, is_callable(memb[1])))
            if (self._show_callables or not is_callable(memb[1])) \
            and (self._show_special_attributes or not is_special_attribute(memb[0])):
                obj_members.append(memb)
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
        # logger.debug("Inserting: {} = {!r}".format(obj_name, obj))
        tree_item = TreeItem(parent_item, obj, obj_name, obj_path)
        return tree_item

   
    def populateTree(self, root_obj, root_name='', single_root_node=False):
        """ Fills the tree using a python object. Sets the root_item.
        """
        logger.debug("populateTree with object id = 0x{:x}".format(id(root_obj)))
        
        if single_root_node is True:
            root_parent_item = TreeItem(None, None, '<root_parent>', '<root_parent>') 
            root_parent_item.children_fetched = True
            root_item = self._addTreeItem(root_parent_item, root_obj, root_name, root_name)
            root_parent_item.append_child(root_item)
            self.root_item = root_parent_item
        else:
            self.root_item = self._addTreeItem(None, root_obj, root_name, root_name)
            
            # Fetch all items of the root so we can select the first row in the constructor.
            root_index = self.index(0, 0)
            self.fetchMore(root_index) 
            
        return self.root_item
    
        
    def _resetTree(self):
        """ Empties and re-populates the tree.
        """
        self.beginResetModel()
        self.reset()
        self.root_item = self.populateTree(self._root_obj, self._root_name,
                                           self.show_root_node)
        self.endResetModel()
    
    
    def getShowCallables(self):
        return self._show_callables
        
    def setShowCallables(self, show_callables):
        """ Shows/hides show_callables, which have a __call__ attribute.
            Repopulates the tree.
        """
        logger.debug("setShowCallables: {}".format(show_callables))
        self._show_callables = show_callables
        self._resetTree()
    

    def getShowSpecialAttributes(self):
        return self._show_special_attributes
        
    def setShowSpecialAttributes(self, show_special_attributes):
        """ Shows/hides special attributes, which begin with an underscore.
            Repopulates the tree.
        """
        logger.debug("setShowSpecialAttributes: {}".format(show_special_attributes))
        self._show_special_attributes = show_special_attributes
        self._resetTree()
        
    def getShowRootNode(self):
        return self.show_root_node


        
