==========
objbrowser
==========

Extensible Python object browser implemented in Qt.

Shows an object in a tree view so that you can inspect its attributes
recursively (e.g. browse through a list of dictionaries).

Requires: PySide (https://github.com/PySide/pyside-setup)

Installation: pip install objbrowser

Example use:

::

    from objbrowser import browse
    a = 16; b = 'hello'
    browse(locals())

For more examples at: see: https://github.com/titusjan/objbrowser

