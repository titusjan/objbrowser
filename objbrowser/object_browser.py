""" 
   Program that shows the local Python environment using the inspect module
"""
from __future__ import print_function
import os, logging, pprint, inspect
from PySide import QtCore, QtGui
from treemodel import TreeModel

logger = logging.getLogger(__name__)

DEBUGGING = True

PROGRAM_NAME = 'pyobjbrowser'
PROGRAM_VERSION = '0.0.1'
PROGRAM_DIRECTORY = os.path.abspath(os.path.dirname(__file__))
IMAGE_DIRECTORY = PROGRAM_DIRECTORY + '/images/'
ABOUT_MESSAGE = u"""%(prog)s version %(version)s
""" % {"prog": PROGRAM_NAME, "version": PROGRAM_VERSION}


    
class ColumnSettings(object):
    """ Class that stores INITIAL column settings. """
    
    def __init__(self, width=120, visible=True, name=None):
        """ Constructor to set mandatory and default settings) """
        self.name = name
        self.visible = visible
        self.width = width
        self.toggle_action = None  # action to show/hide column
        self.toggle_function = None # function that shows/hides column
        
        
# The main window inherits from a Qt class, therefore it has many 
# ancestors public methods and attributes.
# pylint: disable=R0901, R0902, R0904 

class ObjectBrowser(QtGui.QMainWindow):
    """ Object browser main application window.
    """
    def __init__(self, obj = None, obj_name = '', 
                 show_special_methods = True, 
                 width = None, height = None):
        """ Constructor
        
            :param obj: any python object or variable
            :param obj_name: name of the object as it will appear in the root node
            :param show_special_methods: if True the objects special methods, 
                i.e. methods with a name that starts and ends with two underscores, 
                will be displayed (in grey). If False they are hidden.
            :param width: if width and heigth are set, the main windows is resized. 
            :param height: if width and heigth are set, the main windows is resized.
        """
        super(ObjectBrowser, self).__init__()
        
        # Model
        self._tree_model = TreeModel(obj, obj_name = obj_name, 
                                     show_special_methods=show_special_methods)
        
        # Table columns
        self.col_settings = [None] * TreeModel.N_COLS
        self.col_settings[TreeModel.COL_PATH]      = ColumnSettings(visible=True,  width=350)
        self.col_settings[TreeModel.COL_NAME]      = ColumnSettings(visible=True,  width=150)
        self.col_settings[TreeModel.COL_VALUE]     = ColumnSettings(visible=True,  width=150)
        self.col_settings[TreeModel.COL_TYPE]      = ColumnSettings(visible=False, width=150)
        self.col_settings[TreeModel.COL_CLASS]     = ColumnSettings(visible=True,  width=150)
        self.col_settings[TreeModel.COL_ID]        = ColumnSettings(visible=False,  width=150)
        self.col_settings[TreeModel.COL_PREDICATE] = ColumnSettings(visible=False,  width=150)
        #self.col_settings[TreeModel.COL_STR]       = ColumnSettings(visible=False, width=300)
        #self.col_settings[TreeModel.COL_REPR]      = ColumnSettings(visible=True,  width=300)
        for idx, header in enumerate(TreeModel.HEADERS):
            self.col_settings[idx].name = header
        
        # Views
        self._setup_actions()
        self._setup_menu()
        self._setup_views()
        self.setWindowTitle("{} - {}".format(PROGRAM_NAME, obj_name))
        app = QtGui.QApplication.instance()
        app.lastWindowClosed.connect(app.quit) 
        
        # Update views with model
        for settings in self.col_settings:
            settings.toggle_action.setChecked(settings.visible)

        #self.obj_tree.expandToDepth(0)
        
        if width and height:
            self.resize(width, height)


    def _setup_actions(self):
        """ Creates the MainWindow actions.
        """
        # Create actions for the table columns from its settings.
        for col_idx, settings in enumerate(self.col_settings):
            settings.toggle_action = \
                QtGui.QAction("Show {} Column".format(settings.name), 
                              self, checkable=True, checked=True,
                              statusTip = "Shows or hides the {} column".format(settings.name))
            if col_idx >= 0 and col_idx <= 9:
                settings.toggle_action.setShortcut("Ctrl+{:d}".format(col_idx))
            settings.toggle_function = self._make_show_column_function(col_idx) # keep reference
            assert settings.toggle_action.toggled.connect(settings.toggle_function)
            
        self.toggle_special_method_action = \
            QtGui.QAction("Show __special_methods__".format(settings.name), 
                          self, checkable=True, checked=True,
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
        for _idx, settings in enumerate(self.col_settings):
            view_menu.addAction(settings.toggle_action)
        view_menu.addSeparator()
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
        
        for idx, settings in enumerate(self.col_settings):
            #logger.debug("resizing {}: {:d}".format(settings.name, settings.width))
            self.obj_tree.header().resizeSection(idx, settings.width)
        
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

        def create_radio(description):
            "Adds a new radio button to the radio_layout"
            radio_button = QtGui.QRadioButton(description)
            radio_button.toggled.connect(self._change_details_field)
            radio_layout.addWidget(radio_button) 
            return radio_button
        
        self.radio_str            = create_radio("str")
        self.radio_repr           = create_radio("repr")
        self.radio_pretty         = create_radio("pretty print")
        self.radio_doc            = create_radio("doc string")
        self.radio_getdoc         = create_radio("inspect.getdoc")
        self.radio_getcomments    = create_radio("inspect.getcomments")
        self.radio_getfile        = create_radio("inspect.getfile")
        self.radio_getmodule      = create_radio("inspect.getmodule")
        self.radio_getsourcefile  = create_radio("inspect.getsourcefile")
        self.radio_getsourcelines = create_radio("inspect.getsourcelines")
        self.radio_getsource      = create_radio("inspect.getsource")
        
        self.radio_str.setChecked(True)
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
    # pylint: enable=W0201

    def my_test(self):
        """ Function for testing """
        logger.debug("my_test")
        

    @QtCore.Slot(QtCore.QModelIndex, QtCore.QModelIndex)
    def _update_details(self, current_index, _previous_index):
        """ Shows the object details in the editor given an index.
        """
        tree_item = self._tree_model.treeItem(current_index)
        self._update_details_for_item(tree_item)


    def _change_details_field(self):
        """ Changes the field that is changed in the details pane
        """
        current_index = self.obj_tree.selectionModel().currentIndex()
        tree_item = self._tree_model.treeItem(current_index)
        self._update_details_for_item(tree_item)
        
            
    def _update_details_for_item(self, tree_item):
        """ Shows the object details in the editor given an tree_item
        """
        obj = tree_item.obj
        if self.radio_str.isChecked():
            data = str(obj)
        elif self.radio_repr.isChecked():
            data = repr(obj)
        elif self.radio_doc.isChecked():
            try:
                data = obj.__doc__
            except AttributeError:
                data = '<no doc string found>'
        elif self.radio_pretty.isChecked():
            pp = pprint.PrettyPrinter(indent=4)
            data = pp.pformat(obj)
        elif self.radio_getdoc.isChecked():
            data = inspect.getdoc(obj)
            
        elif self.radio_getcomments.isChecked():
            data = inspect.getcomments(obj)
        elif self.radio_getfile.isChecked():
            try:
                data = inspect.getfile(obj)
            except TypeError:
                data = ''
        elif self.radio_getmodule.isChecked():
            try:
                data = inspect.getmodule(obj)
            except TypeError:
                data = ''
        elif self.radio_getsourcefile.isChecked():
            data = inspect.getsourcefile(obj)
        elif self.radio_getsourcelines.isChecked():
            data = inspect.getsourcelines(obj)
        elif self.radio_getsource.isChecked():
            try:
                data = inspect.getsource(obj)
            except IOError:
                data = ''
        else:
            assert False, "No radio button checked."
                
        self.editor.setPlainText(data)

    
    def _make_show_column_function(self, column_idx):
        """ Creates a function that shows or hides a column."""
        show_column = lambda checked: self.obj_tree.setColumnHidden(column_idx, not checked)
        return show_column
    
    
    def toggle_special_methods(self, checked):
        """ Shows/hides the special methods, which start and and with two underscores."""
        logger.debug("toggle_special_methods: {}".format(checked))
        self._tree_model.setShowSpecialMethods(checked)


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
