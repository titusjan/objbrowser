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


class TreeItem(object):
    def __init__(self, parent, obj, obj_name, obj_path):
        self.parent_item = parent
        self.obj = obj
        self.obj_name = obj_name
        self.obj_path = obj_path
        self.child_items = []
        self.has_children = True
        self.children_fetched = False

    def __str__(self):
        return "item: {} {}".format(self.obj_path, len(self.child_items))

    def __repr__(self):
        return "item: {!r}".format(self.child_items)
    
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

