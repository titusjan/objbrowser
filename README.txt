==========
objbrowser
==========

Extensible Python object inspection tool implemented in Qt.

Displays objects as a tree and allows you can to inspect its attributes
recursively (e.g. browse through a list of dictionaries). You can add 
your own inspection methods as new columns to the tree view, or as radio buttons
to the details pane. Altering existing inspection methods is possible as well.

Requires: PySide (https://github.com/PySide/pyside-setup)

Installation: pip install objbrowser

Example use:

::

    from objbrowser import browse
    a = 16; b = 'hello'
    browse(locals())

For more examples see: https://github.com/titusjan/objbrowser

