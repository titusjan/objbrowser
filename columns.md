Column descriptions
===================

From the View menu you can select some extra columns, for instance the object's _id_ column.
This can also be done by right-clicking on the table header.

The following columns are available:

#### name

The name of the object.


#### path

A path to the data: e.g. `var[1]['a'].item`


#### summary

A summary of the object for regular objects (is empty for non-regular objects such as callables or
modules).


#### unicode

The unicode representation of the object. In Python 2 it uses `unicode`, in Python 3 the `str`
function is used.


#### str

The string representation of the object using the `str` function. In Python 3 there is no
difference with the _unicode_ column.


#### repr

The string representation of the object using the `repr` function.


#### type

Type of the object determined using the builtin `type` function.


#### type name

The name of the class of the object via `obj.__class__.__name__`


#### length

The length of the object using the `len` function.


#### id

The identifier of the object with calculated using the `id` function.


#### is attribute

The object is an attribute of the parent (opposed to e.g. a list element).
Attributes are displayed in _italics_ in the table.

#### is callable

True if the object is callable.  Determined with the `callable` built-in function.
Callable objects are displayed in blue in the table.

#### is routine

True if the object is a user-defined or built-in function or method. Determined with the
`inspect.isroutine` method.


#### inspect predicates

Predicates from the `inspect` module.


#### pretty print

Pretty printed representation of the object using the `pprint` module.


#### doc string

The object's doc string.


#### inspect.getdoc

The object's doc string, cleaned up by `inspect.getdoc`


#### inspect.getcomments

Comments above the object's definition. Retrieved using `inspect.getcomments`


#### inspect.getmodule

The object's module. Retrieved using `inspect.module`


#### inspect.getfile

The object's file. Retrieved using `inspect.getfile`


#### inspect.getsourcefile

The object's file. Retrieved using `inspect.getsourcefile`


#### inspect.getsourcelines

Uses `inspect.getsourcelines` to get a list of source lines for the object.


#### inspect.getsource

The source code of an object retrieved using `inspect.getsource`

