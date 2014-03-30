from distutils.core import setup
from objbrowser.objectbrowser import PROGRAM_VERSION

setup(name = 'objbrowser',
    version = PROGRAM_VERSION, 
    description = 'Python object browser implemented in Qt.',
    long_description = open('README.txt').read(),
    url = 'http://pypi.python.org/pypi/objbrowser/',    
    author = "Pepijn Kenter", 
    author_email = "titusjan@gmail.com", 
    license = 'LICENSE.txt',
    packages = ['objbrowser'],
    install_requires = ['PySide (>=1.1.2)'])

