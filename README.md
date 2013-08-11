objbrowser
==========

Python object browser implemented in Qt.

Shows an object in a tree view so that you can examine its attributes
recursively (e.g. browse through a list of dictionaries).

From the _View_ menu you can select some extra columns, such as the 
_object ID_ column.

The details pane at the bottom shows object properties that do not fit
on one line, such as the docstrings and the output of various functions 
of the _inspect_ module from the Python standard library.


![objbrowser screen shot](screen_shot.png)

#### Installation:

1.	Install PySide:
	http://qt-project.org/wiki/Category:LanguageBindings::PySide
	
2.	Run the installer:

		%> sudo python setup.py install
	
#### Usage examples:
	
To examine a dictionary (or any other Python object).

	from objbrowser import browse
	d = {'hello': 'hallo', 'world': 'wereld'} 
	browse(d, obj_name='d')

If you omit the `obj_name` parameter, the path column will not 
start with the object name but with the item names. 
 
To pause program execution and examine all local variables.
 
	from objbrowser import browse
	from datetime import datetime
	
	def my_fun():
	    now = datetime.utcnow()
	    browse(locals())
	
	my_fun()
		
To open two object browser windows simultaneously.

	from objbrowser import create_object_browser, execute
	loc_browser = create_object_browser(locals(), obj_name = 'locals()')
	glb_browser = create_object_browser(globals(), obj_name = 'globals()')
	execute()

If the `show_special_methods` parameter is False, the objects special methods, 
i.e. methods with a name that starts and ends with two underscores, will be hidden.

If the `width` and `height` parameters are given, the window will be resized. 

	from objbrowser import browse

	browse(range(0, 10), obj_name='list', 
    	   show_special_methods = False,
       	   width = 1000, height = 600) 
       

		
