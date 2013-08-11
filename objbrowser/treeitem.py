
# Based on: PySide examples/itemviews/simpletreemodel
# See: http://harmattan-dev.nokia.com/docs/library/html/qt4/itemviews-simpletreemodel.html

# Disabling the need for docstrings, all methods are tiny.
# pylint: disable=C0111

class TreeItem(object):
    """ Tree node class that can be used to build trees of objects.
    """
    def __init__(self, parent, obj, obj_name, obj_path):
        self.parent_item = parent
        self.obj = obj
        self.obj_name = str(obj_name)
        self.obj_path = str(obj_path)
        self.child_items = []
        self.has_children = True
        self.children_fetched = False

    def __str__(self):
        return "<TreeItem: {} ({:d} children)>".format(self.obj_path, len(self.child_items))

    def __repr__(self):
        return "<TreeItem: {} ({:d} children)>".format(self.obj_path, len(self.child_items))
    
    def append_child(self, item):
        self.child_items.append(item)

    def child(self, row):
        return self.child_items[row]

    def child_count(self):
        return len(self.child_items)

    def parent(self):
        return self.parent_item

    def row(self):
        if self.parent_item:
            return self.parent_item.child_items.index(self)
        else:
            return 0

