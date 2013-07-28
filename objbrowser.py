
""" 
   Program that shows the local python environment using the inspect module
"""
from __future__ import print_function

import sys, argparse, os, logging, types, inspect

from PySide import QtCore, QtGui

logger = logging.getLogger(__name__)

DEBUGGING = True

PROGRAM_NAME = 'pyviewer'
PROGRAM_VERSION = '0.0.1'
PROGRAM_DIRECTORY = os.path.abspath(os.path.dirname(__file__))
IMAGE_DIRECTORY = PROGRAM_DIRECTORY + '/images/'
ABOUT_MESSAGE = u"""%(prog)s version %(version)s
""" % {"prog": PROGRAM_NAME, "version": PROGRAM_VERSION}


# Tree column indices
COL_NAME = 0
COL_VALUE = 1
COL_TYPE = 2
COL_CLASS = 3


# The main window inherits from a Qt class, therefore it has many 
# ancestors public methods and attributes.
# pylint: disable=R0901, R0902, R0904 

        
def class_name(obj):
    """ Returns the name of the class of the object.
        Returns empty string if it cannot be determined, 
        e.g. in old-style classes.
    """
    try:
        return obj.__class__.__name__
    except AttributeError:
        return ''


class ObjectBrowser(QtGui.QMainWindow):
    """ The main application.
    """
    def __init__(self, obj = None):
        """ Constructor
            :param obj: any python object or variable
        """
        super(ObjectBrowser, self).__init__()
        
        # Views
        self._setup_actions()
        self._setup_menu()
        self._setup_views()
        self.setWindowTitle(PROGRAM_NAME)
        
        # Update views with model
        #self.col_name_action.setChecked(False)
        #self.col_class_action.setChecked(False)
        #self.col_value_action.setChecked(False)
        
        self.populate_tree(obj)


    def _setup_actions(self):
        """ Creates the MainWindow actions.
        """  
        self.col_name_action = QtGui.QAction(
            "Show Name Column", self, checkable=True, checked=True,
            statusTip = "Shows or hides the Name column")
        self.col_name_action.setShortcut("Ctrl+1")
        self.col_name_action.toggled.connect(self.show_name_column)
                
        self.col_value_action = QtGui.QAction(
            "Show Value Column", self, checkable=True, checked=True,
            statusTip = "Shows or hides the Value column")
        self.col_value_action.setShortcut("Ctrl+2")
        self.col_value_action.toggled.connect(self.show_value_column)

        self.col_type_action = QtGui.QAction(
            "Show Type Column", self, checkable=True, checked=True,
            statusTip = "Shows or hides the Type column")
        self.col_type_action.setShortcut("Ctrl+3")
        self.col_type_action.toggled.connect(self.show_type_column)
        
        self.col_class_action = QtGui.QAction(
            "Show Class Column", self, checkable=True, checked=True,
            statusTip = "Shows or hides the Class column")
        self.col_class_action.setShortcut("Ctrl+4")
        self.col_class_action.toggled.connect(self.show_class_column)
                              
                              
    def _setup_menu(self):
        """ Sets up the main menu.
        """
        file_menu = self.menuBar().addMenu("&File")
        file_menu.addAction("C&lose", self.close_window, "Ctrl+W")
        file_menu.addAction("E&xit", self.quit_application, "Ctrl+Q")
        if DEBUGGING is True:
            file_menu.addSeparator()
            file_menu.addAction("&Test", self.my_test, "Ctrl+T")
        
        view_menu = self.menuBar().addMenu("&View")
        view_menu.addAction(self.col_name_action)        
        view_menu.addAction(self.col_class_action)        
        view_menu.addAction(self.col_value_action)        
        view_menu.addAction(self.col_type_action)        
        
        self.menuBar().addSeparator()
        help_menu = self.menuBar().addMenu("&Help")
        help_menu.addAction('&About', self.about)


    def _setup_views(self):
        """ Creates the UI widgets. 
        """
        central_splitter = QtGui.QSplitter(self, orientation = QtCore.Qt.Vertical)
        self.setCentralWidget(central_splitter)
        central_layout = QtGui.QHBoxLayout()
        central_splitter.setLayout(central_layout)
        
        # Tree widget
        self.obj_tree = QtGui.QTreeWidget()
        #self.obj_tree.setColumnCount(2)
        
        DEF_COL_WIDTH = 200 
        self.obj_tree.setHeaderLabels(["Name", "Value", "Type", "Class"])
        self.obj_tree.header().resizeSection(COL_NAME, DEF_COL_WIDTH)
        self.obj_tree.header().resizeSection(COL_VALUE, DEF_COL_WIDTH)
        self.obj_tree.header().resizeSection(COL_TYPE, DEF_COL_WIDTH)
        self.obj_tree.header().resizeSection(COL_CLASS, DEF_COL_WIDTH)
        
        # Don't stretch last column, it doesn't play nice when columns are 
        # hidden and then shown again
        self.obj_tree.header().setStretchLastSection(False) 
        central_layout.addWidget(self.obj_tree)

        # Editor widget
        font = QtGui.QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(14)

        self.editor = QtGui.QPlainTextEdit()
        self.editor.setReadOnly(True)
        self.editor.setFont(font)
        self.editor.setWordWrapMode(QtGui.QTextOption.NoWrap)
        central_layout.addWidget(self.editor)
        
        # Splitter parameters
        central_splitter.setCollapsible(0, False)
        central_splitter.setCollapsible(1, True)
        central_splitter.setSizes([400, 200])
        central_splitter.setStretchFactor(0, 0)
        central_splitter.setStretchFactor(1, 70)
               
        # Connect signals
        self.obj_tree.currentItemChanged.connect(self.update_details)


    # End of setup_methods
    # pylint: enable=W0201


   
    
    def populate_tree(self, obj):
        """ Fills the tree using a python object.
        """
        logger.debug("populate_tree with object id = 0x{:x}".format(id(obj)))
        obj_type = type(obj)
        parent_item = self.obj_tree
        
        if obj_type == types.DictionaryType:
            for key, value in sorted(obj.iteritems()):
                tree_item = QtGui.QTreeWidgetItem(parent_item)                
                logger.debug("Inserting: {}".format(key))
                tree_item.setText(COL_NAME, key)
                tree_item.setText(COL_VALUE, repr(value))
                tree_item.setText(COL_TYPE, str(type(value)))
                tree_item.setText(COL_CLASS, class_name(value))
        else:
            logger.warn("Unexpected object type: {}".format(obj_type))
            
        #self.obj_tree.expandToDepth(1)

        
 
    @QtCore.Slot(QtGui.QTreeWidgetItem, QtGui.QTreeWidgetItem)
    def update_details(self, current_item, _previous_item):
        """ Highlights the node if it has line:col information.
        """
        #self.editor.clear()
        self.editor.setPlainText(current_item.text(COL_VALUE))

    @QtCore.Slot(int)
    def show_name_column(self, checked):
        """ Shows or hides the name column"""
        self.obj_tree.setColumnHidden(COL_NAME, not checked)                

    @QtCore.Slot(int)
    def show_value_column(self, checked):
        """ Shows or hides the value column"""
        self.obj_tree.setColumnHidden(COL_VALUE, not checked)                

    @QtCore.Slot(int)
    def show_type_column(self, checked):
        """ Shows or hides the type column"""
        self.obj_tree.setColumnHidden(COL_TYPE, not checked)                

    @QtCore.Slot(int)
    def show_class_column(self, checked):
        """ Shows or hides the class column"""
        self.obj_tree.setColumnHidden(COL_CLASS, not checked)                


    def my_test(self):
        """ Function for testing """
        logger.debug("my_test")

    def about(self):
        """ Shows the about message window. """
        QtGui.QMessageBox.about(self, "About %s" % PROGRAM_NAME, ABOUT_MESSAGE)

    def close_window(self):
        """ Closes the window """
        self.close()
        
    def quit_application(self):
        """ Closes all windows """
        app = QtGui.QApplication.instance()
        app.closeAllWindows()

# pylint: enable=R0901, R0902, R0904        


def call_viewer_test():
    """ Test procedure. 
    """
    logger.debug("start call_viewer_test")
    
    class OldStyleClass: pass
    
    class NewStyleClass(object): pass
    
    d = {'4': 44, 's': 11}
    a = 6
    b = 'seven'
    n = None
    lst = [4, '4', d, ['r', dir]]
    
    env = locals()
    logger.debug("locals: {}".format(env))
    
    obj_browser = ObjectBrowser(obj = env)
    obj_browser.resize(1000, 600)
    obj_browser.show()
    
    logger.debug("end call_viewer_test")
    return obj_browser # to keep a reference

        
def main():
    """ Main program to test stand alone 
    """
    app = QtGui.QApplication(sys.argv)
    
    parser = argparse.ArgumentParser(description='Python abstract syntax tree viewer')
    parser.add_argument(dest='file_name', help='Python input file', nargs='?')
    parser.add_argument('-l', '--log-level', dest='log_level', default = 'debug', 
        help = "Log level. Only log messages with a level higher or equal than this "
            "will be printed. Default: 'debug'",
        choices = ('debug', 'info', 'warn', 'error', 'critical'))
    
    args = parser.parse_args()

    logging.basicConfig(level = args.log_level.upper(), 
        format='%(filename)20s:%(lineno)-4d : %(levelname)-7s: %(message)s')

    logger.info('Started {}'.format(PROGRAM_NAME))
    _obj_browser = call_viewer_test() # to keep a reference
    exit_code = app.exec_()
    logging.info('Done {}'.format(PROGRAM_NAME))
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
