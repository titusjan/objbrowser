""" Object browser GUI in Qt
"""
# TODO:
# What to do when getmembers fails
# call get_set descriptors (getters) in summary column.
# ufuncs?
# tool-tips
# sphynx

# qtpy

from __future__ import absolute_import
from __future__ import print_function
import logging, traceback, hashlib, sys


from qtpy import QtCore, QtGui, QtWidgets
from qtpy.QtCore import Slot

from objbrowser.app import get_qapp, get_qsettings, start_qt_event_loop
from objbrowser.version import PROGRAM_NAME, PROGRAM_VERSION, PROGRAM_URL, DEBUGGING
from objbrowser.version import PYTHON_VERSION, QT_API_NAME, QT_API, QTPY_VERSION
from objbrowser.utils import setting_str_to_bool
from objbrowser.treemodel import TreeProxyModel, TreeModel
from objbrowser.toggle_column_mixin import ToggleColumnTreeView
from objbrowser.attribute_model import DEFAULT_ATTR_COLS, DEFAULT_ATTR_DETAILS

logger = logging.getLogger(__name__)


# The main window inherits from a Qt class, therefore it has many 
# ancestors public methods and attributes.
# pylint: disable=R0901, R0902, R0904, W0201 

# It's not possible to use locals() as default for obj by taking take the locals
# from one stack frame higher; you can't know if the ObjectBrowser.__init__ was
# called directly, via the browse() wrapper or via a descendants' constructor.

class ObjectBrowser(QtWidgets.QMainWindow):
    """ Object browser main application window.
    """
    _q_app = None   # Reference to the global application.
    _browsers = []  # Keep lists of browser windows.
    
    def __init__(self, obj,
                 name = '',
                 attribute_columns = DEFAULT_ATTR_COLS,
                 attribute_details = DEFAULT_ATTR_DETAILS,
                 show_callable_attributes = None,  # None uses value from QSettings
                 show_special_attributes = None,  # None uses value from QSettings
                 auto_refresh=None,  # None uses value from QSettings
                 refresh_rate=None,  # None uses value from QSettings
                 reset = False):
        """ Constructor
        
            :param obj: any Python object or variable
            :param name: name of the object as it will appear in the root node
            :param attribute_columns: list of AttributeColumn objects that define which columns
                are present in the table and their defaults
            :param attribute_details: list of AttributeDetails objects that define which attributes
                can be selected in the details pane.
            :param show_callable_attributes: if True rows where the 'is attribute' and 'is callable'
                columns are both True, are displayed. Otherwise they are hidden. 
            :param show_special_attributes: if True rows where the 'is attribute' is True and
                the object name starts and ends with two underscores, are displayed. Otherwise 
                they are hidden.
            :param auto_refresh: If True, the contents refershes itsef every <refresh_rate> seconds.
            :param refresh_rate: number of seconds between automatic refreshes. Default = 2 .
            :param reset: If true the persistent settings, such as column widths, are reset. 
        """
        super(ObjectBrowser, self).__init__()

        self._instance_nr = self._add_instance()
        
        # Model
        self._attr_cols = attribute_columns
        self._attr_details = attribute_details
        
        (self._auto_refresh, self._refresh_rate, show_callable_attributes, show_special_attributes) = \
            self._readModelSettings(reset = reset,
                                    auto_refresh = auto_refresh,
                                    refresh_rate = refresh_rate,
                                    show_callable_attributes= show_callable_attributes,
                                    show_special_attributes = show_special_attributes)

        self._tree_model = TreeModel(obj, name, attr_cols = self._attr_cols)
            
        self._proxy_tree_model = TreeProxyModel(
            show_callable_attributes= show_callable_attributes,
            show_special_attributes = show_special_attributes)
        
        self._proxy_tree_model.setSourceModel(self._tree_model)
        #self._proxy_tree_model.setSortRole(RegistryTableModel.SORT_ROLE)
        self._proxy_tree_model.setDynamicSortFilter(True) 
        #self._proxy_tree_model.setSortCaseSensitivity(Qt.CaseInsensitive)
                
        # Views
        self._setup_actions()
        self._setup_menu()
        self._setup_views()
        self.setWindowTitle("{} - {}".format(PROGRAM_NAME, name))

        self._readViewSettings(reset = reset)

        assert self._refresh_rate > 0, "refresh_rate must be > 0. Got: {}".format(self._refresh_rate)
        self._refresh_timer = QtCore.QTimer(self)
        self._refresh_timer.setInterval(self._refresh_rate * 1000)
        self._refresh_timer.timeout.connect(self.refresh)
        
        # Update views with model
        self.toggle_special_attribute_action.setChecked(show_special_attributes)
        self.toggle_callable_action.setChecked(show_callable_attributes)
        self.toggle_auto_refresh_action.setChecked(self._auto_refresh)
     
        # Select first row so that a hidden root node will not be selected.
        first_row_index = self._proxy_tree_model.firstItemIndex()
        self.obj_tree.setCurrentIndex(first_row_index)
        if self._tree_model.inspectedNodeIsVisible:
            self.obj_tree.expand(first_row_index)
        

    def refresh(self):
        """ Refreshes object brawser contents
        """
        logger.debug("Refreshing")
        self._tree_model.refreshTree()
        
        
    def _add_instance(self):
        """ Adds the browser window to the list of browser references.
            If a None is present in the list it is inserted at that position, otherwise
            it is appended to the list. The index number is returned.
            
            This mechanism is used so that repeatedly creating and closing windows does not
            increase the instance number, which is used in writing the persistent settings.
        """
        try:
            idx = self._browsers.index(None)
        except ValueError:
            self._browsers.append(self)
            idx = len(self._browsers) - 1
        else:
            self._browsers[idx] = self

        return idx


    def _remove_instance(self):
        """ Sets the reference in the browser list to None. 
        """
        idx = self._browsers.index(self)
        self._browsers[idx] = None
        
            
    def _make_show_column_function(self, column_idx):
        """ Creates a function that shows or hides a column."""
        show_column = lambda checked: self.obj_tree.setColumnHidden(column_idx, not checked)
        return show_column            


    def _setup_actions(self):
        """ Creates the main window actions.
        """
        # Show/hide callable objects
        self.toggle_callable_action = \
            QtWidgets.QAction("Show callable attributes", self, checkable=True,
                          shortcut = QtGui.QKeySequence("Alt+C"),
                          statusTip = "Shows/hides attributes that are callable (functions, methods, etc)")
        self.toggle_callable_action.toggled.connect(self._proxy_tree_model.setShowCallables)
                              
        # Show/hide special attributes
        self.toggle_special_attribute_action = \
            QtWidgets.QAction("Show __special__ attributes", self, checkable=True,
                          shortcut = QtGui.QKeySequence("Alt+S"),
                          statusTip = "Shows or hides __special__ attributes")
        self.toggle_special_attribute_action.toggled.connect(self._proxy_tree_model.setShowSpecialAttributes)

        # Toggle auto-refresh on/off
        self.toggle_auto_refresh_action = \
            QtWidgets.QAction("Auto-refresh", self, checkable=True,
                          statusTip = "Auto refresh every {} seconds".format(self._refresh_rate))
        self.toggle_auto_refresh_action.toggled.connect(self.toggle_auto_refresh)
                              
        # Add another refresh action with a different short cut. An action must be added to
        # a visible widget for it to receive events. It is added to the main windows to prevent it
        # from being displayed again in the menu
        self.refresh_action_f5 = QtWidgets.QAction(self, text="&Refresh2", shortcut="F5")
        self.refresh_action_f5.triggered.connect(self.refresh)
        self.addAction(self.refresh_action_f5) 
        
        # My test action.
        self.my_test_action = \
            QtWidgets.QAction("My test", self, checkable=False,
                          statusTip = "Test action for debugging")
        self.my_test_action.toggled.connect(self.my_test)


    def _setup_menu(self):
        """ Sets up the main menu.
        """
        file_menu = self.menuBar().addMenu("&File")
        file_menu.addAction("C&lose", self.close, "Ctrl+W")
        file_menu.addAction("E&xit", self.quit_application, "Ctrl+Q")
        if DEBUGGING is True:
            file_menu.addSeparator()
            file_menu.addAction("&Test", self.my_test, "Ctrl+T")
        
        view_menu = self.menuBar().addMenu("&View")
        view_menu.addAction("&Refresh", self.refresh, "Ctrl+R")
        view_menu.addAction(self.toggle_auto_refresh_action)
        
        view_menu.addSeparator()
        self.show_cols_submenu = view_menu.addMenu("Table columns")
        view_menu.addSeparator()
        view_menu.addAction(self.toggle_callable_action)
        view_menu.addAction(self.toggle_special_attribute_action)
        
        self.menuBar().addSeparator()
        help_menu = self.menuBar().addMenu("&Help")
        help_menu.addAction('&About...', self.about)


    def _setup_views(self):
        """ Creates the UI widgets. 
        """
        self.central_splitter = QtWidgets.QSplitter(self, orientation = QtCore.Qt.Vertical)
        self.setCentralWidget(self.central_splitter)

        # Tree widget
        self.obj_tree = ToggleColumnTreeView()
        self.obj_tree.setAlternatingRowColors(True)
        self.obj_tree.setModel(self._proxy_tree_model)
        self.obj_tree.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.obj_tree.setUniformRowHeights(True)
        self.obj_tree.setAnimated(True)
        self.obj_tree.add_header_context_menu()
        
        # Stretch last column? 
        # It doesn't play nice when columns are hidden and then shown again.
        obj_tree_header = self.obj_tree.header()
        obj_tree_header.setSectionsMovable(True)
        obj_tree_header.setStretchLastSection(False)
        for action in self.obj_tree.toggle_column_actions_group.actions():
            self.show_cols_submenu.addAction(action)

        self.central_splitter.addWidget(self.obj_tree)

        # Bottom pane
        bottom_pane_widget = QtWidgets.QWidget()
        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.setSpacing(0)
        bottom_layout.setContentsMargins(5, 5, 5, 5) # left top right bottom
        bottom_pane_widget.setLayout(bottom_layout)
        self.central_splitter.addWidget(bottom_pane_widget)
        
        group_box = QtWidgets.QGroupBox("Details")
        bottom_layout.addWidget(group_box)
        
        group_layout = QtWidgets.QHBoxLayout()
        group_layout.setContentsMargins(2, 2, 2, 2) # left top right bottom
        group_box.setLayout(group_layout)
        
        # Radio buttons
        radio_widget = QtWidgets.QWidget()
        radio_layout = QtWidgets.QVBoxLayout()
        radio_layout.setContentsMargins(0, 0, 0, 0) # left top right bottom        
        radio_widget.setLayout(radio_layout) 

        self.button_group = QtWidgets.QButtonGroup(self)
        for button_id, attr_detail in enumerate(self._attr_details):
            radio_button = QtWidgets.QRadioButton(attr_detail.name)
            radio_layout.addWidget(radio_button)
            self.button_group.addButton(radio_button, button_id)

        self.button_group.buttonClicked[int].connect(self._change_details_field)
        self.button_group.button(0).setChecked(True)
                
        radio_layout.addStretch(1)
        group_layout.addWidget(radio_widget)

        # Editor widget
        font = QtGui.QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        #font.setPointSize(14)

        self.editor = QtWidgets.QPlainTextEdit()
        self.editor.setReadOnly(True)
        self.editor.setFont(font)
        group_layout.addWidget(self.editor)
        
        # Splitter parameters
        self.central_splitter.setCollapsible(0, False)
        self.central_splitter.setCollapsible(1, True)
        self.central_splitter.setSizes([400, 200])
        self.central_splitter.setStretchFactor(0, 10)
        self.central_splitter.setStretchFactor(1, 0)
               
        # Connect signals
        # Keep a temporary reference of the selection_model to prevent segfault in PySide.
        # See http://permalink.gmane.org/gmane.comp.lib.qt.pyside.devel/222
        selection_model = self.obj_tree.selectionModel() 
        selection_model.currentChanged.connect(self._update_details)

    # End of setup_methods
    
    
    def _settings_group_name(self, postfix):
        """ Constructs a group name for the persistent settings.
            
            Because the columns in the main table are extendible, we must store the settings
            in a different group if a different combination of columns is used. Therefore the
            settings group name contains a hash that is calculated from the used column names.
            Furthermore the window number is included in the settings group name. Finally a
            postfix string is appended. 
        """
        column_names = ",".join([col.name for col in self._attr_cols])
        settings_str = column_names
        columns_hash = hashlib.md5(settings_str.encode('utf-8')).hexdigest()
        settings_grp = "{}_win{}_{}".format(columns_hash, self._instance_nr, postfix)
        return settings_grp

                
    def _readModelSettings(self,
                           reset=False,
                           auto_refresh = None,
                           refresh_rate = None,
                           show_callable_attributes = None,
                           show_special_attributes = None):
        """ Reads the persistent model settings .
            The persistent settings (show_callable_attributes, show_special_attributes) can be \
            overridden by giving it a True or False value.
            If reset is True and the setting is None, True is used as default.
        """ 
        default_auto_refresh = False
        default_refresh_rate = 2
        default_sra = True
        default_ssa = True
        if reset:
            logger.debug("Resetting persistent model settings")
            if refresh_rate is None:
                refresh_rate = default_refresh_rate
            if auto_refresh is None:
                auto_refresh = default_auto_refresh
            if show_callable_attributes is None:
                show_callable_attributes = default_sra
            if show_special_attributes is None:
                show_special_attributes = default_ssa
        else:
            logger.debug("Reading model settings for window: {:d}".format(self._instance_nr))
            settings = get_qsettings()
            settings.beginGroup(self._settings_group_name('model'))

            if auto_refresh is None:
                auto_refresh = setting_str_to_bool(
                    settings.value("auto_refresh", default_auto_refresh))
            logger.debug("read auto_refresh: {!r}".format(auto_refresh))

            if refresh_rate is None:
                refresh_rate = float(settings.value("refresh_rate", default_refresh_rate))
            logger.debug("read refresh_rate: {!r}".format(refresh_rate))

            if show_callable_attributes is None:
                show_callable_attributes = setting_str_to_bool(
                    settings.value("show_callable_attributes", default_sra))
            logger.debug("read show_callable_attributes: {!r}".format(show_callable_attributes))
                
            if show_special_attributes is None:
                show_special_attributes = setting_str_to_bool(
                    settings.value("show_special_attributes", default_ssa))
            logger.debug("read show_special_attributes: {!r}".format(show_special_attributes))
            
            settings.endGroup()
                        
        return (auto_refresh, refresh_rate, show_callable_attributes, show_special_attributes)
                    
    
    def _writeModelSettings(self):
        """ Writes the model settings to the persistent store
        """         
        logger.debug("Writing model settings for window: {:d}".format(self._instance_nr))
        
        settings = get_qsettings()
        settings.beginGroup(self._settings_group_name('model'))

        logger.debug("writing auto_refresh: {!r}".format(self._auto_refresh))
        settings.setValue("auto_refresh", self._auto_refresh)
        
        logger.debug("writing refresh_rate: {!r}".format(self._refresh_rate))
        settings.setValue("refresh_rate", self._refresh_rate)

        logger.debug("writing show_callable_attributes: {!r}"
                     .format(self._proxy_tree_model.getShowCallables()))
        settings.setValue("show_callable_attributes", self._proxy_tree_model.getShowCallables())

        logger.debug("writing show_special_attributes: {!r}"
                     .format(self._proxy_tree_model.getShowSpecialAttributes()))
        settings.setValue("show_special_attributes", self._proxy_tree_model.getShowSpecialAttributes())
        
        settings.endGroup()
        
    
    def _readViewSettings(self, reset=False):
        """ Reads the persistent program settings
        
            :param reset: If True, the program resets to its default settings
        """ 
        pos = QtCore.QPoint(20 * self._instance_nr, 20 * self._instance_nr)
        window_size = QtCore.QSize(1024, 700)
        details_button_idx = 0
        
        header = self.obj_tree.header()
        header_restored = False
        
        if reset:
            logger.debug("Resetting persistent view settings")
        else:
            logger.debug("Reading view settings for window: {:d}".format(self._instance_nr))
            settings = get_qsettings()
            settings.beginGroup(self._settings_group_name('view'))
            pos = settings.value("main_window/pos", pos)
            window_size = settings.value("main_window/size", window_size)
            details_button_idx = int(settings.value("details_button_idx", details_button_idx))
            splitter_state = settings.value("central_splitter/state")
            if splitter_state:
                self.central_splitter.restoreState(splitter_state) 
            header_restored = self.obj_tree.read_view_settings('table/header_state', 
                                                               settings, reset) 
            settings.endGroup()

        if not header_restored:
            column_sizes = [col.width for col in self._attr_cols]
            column_visible = [col.col_visible for col in self._attr_cols]
        
            for idx, size in enumerate(column_sizes):
                if size > 0: # Just in case 
                    header.resizeSection(idx, size)
    
            for idx, visible in enumerate(column_visible):
                self.obj_tree.toggle_column_actions_group.actions()[idx].setChecked(visible)  
            
        self.resize(window_size)
        self.move(pos)
        button = self.button_group.button(details_button_idx)
        if button is not None:
            button.setChecked(True)



    def _writeViewSettings(self):
        """ Writes the view settings to the persistent store
        """         
        logger.debug("Writing view settings for window: {:d}".format(self._instance_nr))
        
        settings = get_qsettings()
        settings.beginGroup(self._settings_group_name('view'))
        self.obj_tree.write_view_settings("table/header_state", settings)
        settings.setValue("central_splitter/state", self.central_splitter.saveState())
        settings.setValue("details_button_idx", self.button_group.checkedId())
        settings.setValue("main_window/pos", self.pos())
        settings.setValue("main_window/size", self.size())
        settings.endGroup()
            

    @Slot(QtCore.QModelIndex, QtCore.QModelIndex)
    def _update_details(self, current_index, _previous_index):
        """ Shows the object details in the editor given an index.
        """
        tree_item = self._proxy_tree_model.treeItem(current_index)
        self._update_details_for_item(tree_item)

        
    def _change_details_field(self, _button_id=None):
        """ Changes the field that is displayed in the details pane
        """
        #logger.debug("_change_details_field: {}".format(_button_id))
        current_index = self.obj_tree.selectionModel().currentIndex()
        tree_item = self._proxy_tree_model.treeItem(current_index)
        self._update_details_for_item(tree_item)
        
            
    def _update_details_for_item(self, tree_item):
        """ Shows the object details in the editor given an tree_item
        """
        self.editor.setStyleSheet("color: black;")
        try:
            #obj = tree_item.obj
            button_id = self.button_group.checkedId()
            assert button_id >= 0, "No radio button selected. Please report this bug."
            attr_details = self._attr_details[button_id]
            data = attr_details.data_fn(tree_item)
            self.editor.setPlainText(data)
            self.editor.setWordWrapMode(attr_details.line_wrap)
            
        except Exception as ex:
            self.editor.setStyleSheet("color: red;")
            stack_trace = traceback.format_exc()
            self.editor.setPlainText("{}\n\n{}".format(ex, stack_trace))
            self.editor.setWordWrapMode(QtWidgets.QTextOption.WrapAtWordBoundaryOrAnywhere)

    def toggle_auto_refresh(self, checked):
        """ Toggles auto-refresh on/off.
        """
        if checked:
            logger.info("Auto-refresh on. Rate {:g} seconds".format(self._refresh_rate))
            self._refresh_timer.start()
        else:
            logger.info("Auto-refresh off")
            self._refresh_timer.stop()
        self._auto_refresh = checked        


    def my_test(self):
        """ Function for testing """
        logger.debug("my_test")

        self._tree_model.beginResetModel()
        self._tree_model.endResetModel()

        
    def about(self):
        """ Shows the about message window. """
        message = ("{}: {}\n\nPython: {}\n{} (api: {}, qtpy: {})\n\n{}"
                   .format(PROGRAM_NAME, PROGRAM_VERSION, PYTHON_VERSION,
                           QT_API_NAME, QT_API, QTPY_VERSION, PROGRAM_URL))
        QtWidgets.QMessageBox.about(self, "About {}".format(PROGRAM_NAME), message)


    def _finalize(self):
        """ Cleans up resources when this window is closed.
            Disconnects all signals for this window.
        """
        self._refresh_timer.stop()
        self._refresh_timer.timeout.disconnect(self.refresh)
        self.toggle_callable_action.toggled.disconnect(self._proxy_tree_model.setShowCallables)
        self.toggle_special_attribute_action.toggled.disconnect(self._proxy_tree_model.setShowSpecialAttributes)        
        self.toggle_auto_refresh_action.toggled.disconnect(self.toggle_auto_refresh)
        self.refresh_action_f5.triggered.disconnect(self.refresh)
        self.button_group.buttonClicked[int].disconnect(self._change_details_field)
        selection_model = self.obj_tree.selectionModel() 
        selection_model.currentChanged.disconnect(self._update_details)
        
        
    def closeEvent(self, event):
        """ Called when the window is closed
        """
        logger.debug("closeEvent")
        self._writeModelSettings()                
        self._writeViewSettings()
        self._finalize()                
        self.close()
        event.accept()
        self._remove_instance()
        logger.debug("Closed {} window {}".format(PROGRAM_NAME, self._instance_nr))


    def quit_application(self):
        """ Closes all windows """
        logger.debug("Closing all windows")
        get_qapp().closeAllWindows()


    @classmethod
    def about_to_quit(cls):
        """ Called when application is about to quit
        """
        # Sanity check
        for idx, bw in enumerate(cls._browsers):
            if bw is not None:
                raise AssertionError("Reference not cleaned up: {}".format(idx))

        logger.debug("Quitting {}".format(PROGRAM_NAME))
        
            
    @classmethod
    def create_browser(cls, *args, **kwargs):
        """ Creates and shows and ObjectBrowser window.
        
            Creates the Qt Application object if it doesn't yet exist.
            
            The *args and **kwargs will be passed to the ObjectBrowser constructor.
            
            A (class attribute) reference to the browser window is kept to prevent it from being
            garbage-collected.
        """
        q_app = QtWidgets.QApplication.instance()
        if q_app is None:

            logger.debug("Creating QApplication instance")
            q_app = QtWidgets.QApplication(sys.argv)
            q_app.aboutToQuit.connect(cls.about_to_quit)
            q_app.lastWindowClosed.connect(q_app.quit)
        else:
            logger.debug("Reusing existing QApplication instance")
            
        cls._q_app = q_app # keeping reference to prevent garbage collection. 
        
        object_browser = cls(*args, **kwargs)
        object_browser.show()
        object_browser.raise_()
        return object_browser

    
    @classmethod
    def execute(cls):
        """ Start the Qt event loop.
        """
        assert cls._q_app is not None, "QApplication object doesn't exist yet."
        exit_code = start_qt_event_loop(cls._q_app)
        return exit_code
    
    
    @classmethod
    def browse(cls, *args, **kwargs):
        """ Create and run object browser.
            For this, the following three steps are done:
            1) Create QApplication object if it doesn't yet exist
            2) Create and show an ObjectBrowser window
            3) Start the Qt event loop.
        
            The *args and **kwargs will be passed to the ObjectBrowser constructor.
        """
        logger.info("Browsing with {} {}".format(PROGRAM_NAME, PROGRAM_VERSION))
        logger.info("Using Python {}".format(PYTHON_VERSION))
        logger.info("Using {} (api {}, qtpy: {})".format(QT_API_NAME, QT_API, QTPY_VERSION))

        cls.create_browser(*args, **kwargs)
        exit_code = cls.execute()
        return exit_code
        