""" 
   Program that shows the local Python environment using the inspect module
   # TODO: show items configurable
   # TODO: persistent settings.
   # TODO: show items if object has iteritems()
   # TODO: repr column
   # TODO: unicode
   # TODO: look at QStandardItemModel
   # TODO: show root node <--> obj_name is None ?
   # TODO: word wrap in attribute details
   # TODO: tool-tips
   # TODO: python 3
   # TODO: zebra striping.
"""
from __future__ import absolute_import
from __future__ import print_function
import os, logging, traceback
from PySide import QtCore, QtGui

from objbrowser.treemodel import TreeModel
from objbrowser.attribute_column import DEFAULT_ATTR_COLUMNS
from objbrowser.attribute_detail import DEFAULT_ATTR_DETAILS

logger = logging.getLogger(__name__)

DEBUGGING = True

PROGRAM_NAME = 'pyobjbrowser'
PROGRAM_VERSION = '0.9.1'
PROGRAM_DIRECTORY = os.path.abspath(os.path.dirname(__file__))
IMAGE_DIRECTORY = PROGRAM_DIRECTORY + '/images/'
ABOUT_MESSAGE = u"""%(prog)s version %(version)s
""" % {"prog": PROGRAM_NAME, "version": PROGRAM_VERSION}

        
# The main window inherits from a Qt class, therefore it has many 
# ancestors public methods and attributes.
# pylint: disable=R0901, R0902, R0904, W0201 

class ObjectBrowser(QtGui.QMainWindow):
    """ Object browser main application window.
    """
    _n_instances = 0
    
    def __init__(self, 
                 obj = None, 
                 obj_name = '',
                 attr_columns = DEFAULT_ATTR_COLUMNS,  
                 attr_details = DEFAULT_ATTR_DETAILS,  
                 show_callables = True,
                 show_special_methods = True, 
                 show_root_node = False, 
                 width = 1200, height = 800):
        """ Constructor
        
            :param obj: any Python object or variable
            :param obj_name: name of the object as it will appear in the root node
            :param show_callables: if True the callables objects, 
                i.e. objects (such as function) that  a __call__ method, 
                will be displayed (in brown). If False they are hidden.
            :param show_special_methods: if True the objects special methods, 
                i.e. methods with a name that starts and ends with two underscores, 
                will be displayed (in grey). If False they are hidden.
            :param width: if width and height are set, the main windows is resized. 
            :param height: if width and height are set, the main windows is resized.
        """
        super(ObjectBrowser, self).__init__()

        ObjectBrowser._n_instances += 1
        self._instance_nr = self._n_instances        
        
        # Model
        self._attr_cols = attr_columns
        self._attr_details = attr_details
        
        self._tree_model = TreeModel(obj, 
                                     root_obj_name = obj_name,
                                     attr_cols = self._attr_cols,  
                                     show_root_node = show_root_node,
                                     show_callables = show_callables, 
                                     show_special_methods = show_special_methods)
        
        # Views
        self._setup_actions()
        self._setup_menu()
        self._setup_views()
        self.setWindowTitle("{} - {}".format(PROGRAM_NAME, obj_name))
        app = QtGui.QApplication.instance()
        app.lastWindowClosed.connect(app.quit) 

        self._readSettings()
        
        # Update views with model
        for action, attr_col in zip(self.toggle_column_actions, self._attr_cols):
            action.setChecked(attr_col.visible)
            
        if show_root_node is True:
            self.obj_tree.expandToDepth(0)
     
        # Select first row so that a hidden root node will not be selected.
        first_row = self._tree_model.first_item_index()
        self.obj_tree.setCurrentIndex(first_row)
        
            
            
    def _make_show_column_function(self, column_idx):
        """ Creates a function that shows or hides a column."""
        show_column = lambda checked: self.obj_tree.setColumnHidden(column_idx, not checked)
        return show_column            


    def _setup_actions(self):
        """ Creates the main window actions.
        """
        # Show/hide table column actions
        self.toggle_column_actions = []
        self.__toggle_functions = []  # for keeping references
        for col_idx, attr_col in enumerate(self._attr_cols):
            action = QtGui.QAction("Show {} Column".format(attr_col.name), 
                                   self, checkable=True, checked=True,
                                   statusTip = "Shows or hides the {} column".format(attr_col.name))
            self.toggle_column_actions.append(action)
                
            if col_idx >= 0 and col_idx <= 9:
                action.setShortcut("Ctrl+{:d}".format(col_idx))
                
            func = self._make_show_column_function(col_idx) 
            self.__toggle_functions.append(func) # keep reference
            assert action.toggled.connect(func)
            
        # Show/hide callable objects
        self.toggle_callable_action = \
            QtGui.QAction("Show callable objects", self, checkable=True, checked=True,
                          statusTip = "Shows or hides callable objects (functions, methods, etc)")
        assert self.toggle_callable_action.toggled.connect(self.toggle_callables)
                              
        # Show/hide special methods
        self.toggle_special_method_action = \
            QtGui.QAction("Show __special_methods__", self, checkable=True, checked=True,
                          statusTip = "Shows or hides __special_methods__")
        assert self.toggle_special_method_action.toggled.connect(self.toggle_special_methods)
                              
                              
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
        for action in self.toggle_column_actions:
            view_menu.addAction(action)
        view_menu.addSeparator()
        view_menu.addAction(self.toggle_callable_action)
        view_menu.addAction(self.toggle_special_method_action)
        
        self.menuBar().addSeparator()
        help_menu = self.menuBar().addMenu("&Help")
        help_menu.addAction('&About', self.about)


    def _setup_views(self):
        """ Creates the UI widgets. 
        """
        central_splitter = QtGui.QSplitter(self, orientation = QtCore.Qt.Vertical)
        self.setCentralWidget(central_splitter)
        central_layout = QtGui.QVBoxLayout()
        central_splitter.setLayout(central_layout)
        
        # Tree widget
        self.obj_tree = QtGui.QTreeView()
        self.obj_tree.setModel(self._tree_model)
        self.obj_tree.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.obj_tree.setUniformRowHeights(True)
        
        for idx, attr_col in enumerate(self._attr_cols):
            self.obj_tree.header().resizeSection(idx, attr_col.width)
            
        # Stretch last column? 
        # It doesn't play nice when columns are hidden and then shown again.
        self.obj_tree.header().setStretchLastSection(False) 

        central_layout.addWidget(self.obj_tree)

        # Bottom pane
        pane_widget = QtGui.QWidget()
        central_layout.addWidget(pane_widget)
        pane_layout = QtGui.QHBoxLayout()
        pane_widget.setLayout(pane_layout)
        
        # Radio buttons
        group_box = QtGui.QGroupBox("Details")
        radio_layout = QtGui.QVBoxLayout()
        self.button_group = QtGui.QButtonGroup(self) 

        for button_id, attr_detail in enumerate(self._attr_details):
            radio_button = QtGui.QRadioButton(attr_detail.name)
            radio_layout.addWidget(radio_button)
            self.button_group.addButton(radio_button, button_id)

        self.button_group.buttonClicked[int].connect(self._change_details_field)
        self.button_group.button(0).setChecked(True)
                
        radio_layout.addStretch(1)
        group_box.setLayout(radio_layout)
        pane_layout.addWidget(group_box)

        # Editor widget
        font = QtGui.QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(14)

        self.editor = QtGui.QPlainTextEdit()
        self.editor.setReadOnly(True)
        self.editor.setFont(font)
        pane_layout.addWidget(self.editor)
        
        # Splitter parameters
        central_splitter.setCollapsible(0, False)
        central_splitter.setCollapsible(1, True)
        central_splitter.setSizes([400, 200])
        central_splitter.setStretchFactor(0, 10)
        central_splitter.setStretchFactor(1, 0)
               
        # Connect signals
        selection_model = self.obj_tree.selectionModel()
        assert selection_model.currentChanged.connect(self._update_details)

    # End of setup_methods
    
    def _readSettings(self, reset=False):
        """ Reads the persistent program settings
        
            :param reset: If True, the program resets to its default settings
        """ 
        logger.debug("Reading settings window: {:d}".format(self._instance_nr))
        
        settings = QtCore.QSettings()
        settings.beginGroup("window_{:d}".format(self._instance_nr))
        pos = QtCore.QPoint(20 * self._instance_nr, 20 * self._instance_nr)
        size = QtCore.QSize(1024, 700)
        details_button_idx = 0
        if not reset:
            pos = settings.value("main_window/pos", pos)
            size = settings.value("main_window/size", size)
            details_button_idx = settings.value("main_window/details_button_idx", 
                                                details_button_idx)
        self.resize(size)
        self.move(pos)
        self.button_group.button(details_button_idx).setChecked(True)
        
        if False: 
            self.central_splitter.restoreState(settings.value("self.central_splitter/state"))
            
            header = self.signal_table.horizontalHeader()
            header.restoreState(settings.value("signal_table/header/state"))
            header = self.avg_table.horizontalHeader()
            header.restoreState(settings.value("avg_table/header/state"))
            
        settings.endGroup()


    def _writeSettings(self):
        """ Reads the persistent program settings
        """         
        logger.debug("Writing settings window: {:d}".format(self._instance_nr))
        
        settings = QtCore.QSettings()
        settings.beginGroup("window_{:d}".format(self._instance_nr))
        
        if False:
            header = self.avg_table.horizontalHeader()
            settings.setValue("avg_table/header/state", header.saveState())
            header = self.signal_table.horizontalHeader()
            settings.setValue("signal_table/header/state", header.saveState())
                        
            settings.setValue("self.central_splitter/state", self.central_splitter.saveState())
        
        settings.setValue("main_window/details_button_idx", self.button_group.checkedId())
        settings.setValue("main_window/pos", self.pos())
        settings.setValue("main_window/size", self.size())
        settings.endGroup()
            

    @QtCore.Slot(QtCore.QModelIndex, QtCore.QModelIndex)
    def _update_details(self, current_index, _previous_index):
        """ Shows the object details in the editor given an index.
        """
        tree_item = self._tree_model.treeItem(current_index)
        self._update_details_for_item(tree_item)

        
    def _change_details_field(self, _button_id=None):
        """ Changes the field that is displayed in the details pane
        """
        #logger.debug("_change_details_field: {}".format(_button_id))
        current_index = self.obj_tree.selectionModel().currentIndex()
        tree_item = self._tree_model.treeItem(current_index)
        self._update_details_for_item(tree_item)
        
            
    def _update_details_for_item(self, tree_item):
        """ Shows the object details in the editor given an tree_item
        """
        self.editor.setStyleSheet("color: black;")
        try:
            obj = tree_item.obj
            button_id = self.button_group.checkedId()
            assert button_id >= 0, "No radio button selected. Please report this bug."
            data = self._attr_details[button_id].data_fn(obj)
            self.editor.setPlainText(data)
            
        except StandardError, ex:
            self.editor.setStyleSheet("color: red;")
            stack_trace = traceback.format_exc()
            self.editor.setPlainText("{}\n\n{}".format(ex, stack_trace))
            if DEBUGGING is True:
                raise

    
    def toggle_callables(self, checked):
        """ Shows/hides the special callable objects.
            
            Callable objects are functions, methods, etc. They have a __call__ attribute. 
        """
        logger.debug("toggle_callables: {}".format(checked))
        self._tree_model.setShowCallables(checked)

    def toggle_special_methods(self, checked):
        """ Shows/hides the special methods.
            
            Special methods are objects that have names that start and end with two underscores.
        """
        logger.debug("toggle_special_methods: {}".format(checked))
        self._tree_model.setShowSpecialMethods(checked)

    def my_test(self):
        """ Function for testing """
        logger.debug("my_test")
        
    def about(self):
        """ Shows the about message window. """
        QtGui.QMessageBox.about(self, "About %s" % PROGRAM_NAME, ABOUT_MESSAGE)

    def close_window(self):
        """ Closes the window """
        #self._writeSettings()
        self.close()
        
    def quit_application(self):
        """ Closes all windows """
        app = QtGui.QApplication.instance()
        app.closeAllWindows()

    def closeEvent(self, event):
        """ Close all windows (e.g. the L0 window).
        """
        logger.debug("closeEvent")
        self._writeSettings()                
        self.close()
        event.accept()
            

