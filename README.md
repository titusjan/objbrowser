objbrowser
==========

Python object browser implemented in Qt.

Shows an object in a tree view so that you can examine its attributes
recursively (e.g. browse through a list of dictionaries).

From the _View_ menu you can select some extra columns, for instance the 
objects' _id_ column.

The details pane at the bottom shows object properties that do not fit
on one line, such as the docstrings and the output of various functions 
of the `inspect` module from the Python standard library.


![objbrowser screen shot](screen_shot.png)

#### Installation:

1.	Install PySide:
	http://qt-project.org/wiki/Category:LanguageBindings::PySide
	
2.	Run the installer:

		%> pip install objbrowser
	
#### Usage examples:

Some complete examples can be found in the [examples directory](examples)

The first parameter is the object to be inspected. For example you can 
examine the dictionary with the local variables:

```Python
from objbrowser import browse
a = 67; pi = 3.1415 
browse(locals())
```

The second parameter can be the name of the object. In that case the object
itself will be displayed in the root node.

```Python
browse(locals(), 'locals()')
```

By setting the `show_routine_attributes` and/or the `show_special_attributes` 
parameters you can override the settings from the _View_ menu. The `reset`
parameter resets the persistent window settings (e.g. size and position)

```Python
s1 = 'Hello'
s2 = 'World'

browse({'s1': s1, 's2': s2}, 
        show_routine_attributes = True,
        show_special_attributes = False, 
        reset = True)
```



		
