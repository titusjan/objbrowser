from distutils.core import setup
from objbrowser.objectbrowser import PROGRAM_VERSION

setup(name = 'objbrowser',
    version = PROGRAM_VERSION, 
    author = "Pepijn Kenter", 
    author_email = "titusjan@gmail.com", 
    packages = ['objbrowser'],
    requires = ['PySide (>=1.1.2)'])
