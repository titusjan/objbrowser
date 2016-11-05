#!/usr/bin/env python
# -*- coding: utf-8 -*-

# To make a release type:
#   python setup.py sdist --formats=zip

# Then upload to PiPy with
#   twine upload dist/objbrowser-1.2.0.zip

from distutils.core import setup
from objbrowser.version import DEBUGGING, PROGRAM_VERSION



assert not DEBUGGING, "DEBUGGING must be False"

setup(name = 'objbrowser',
    version = PROGRAM_VERSION, 
    description = 'GUI for Python object introspection.',
    long_description = open('README.txt').read(),
    url = 'https://github.com/titusjan/objbrowser',
    author = "Pepijn Kenter", 
    author_email = "titusjan@gmail.com", 
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: X11 Applications :: Qt',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Adaptive Technologies',
        'Topic :: Software Development',
        'Topic :: Utilities'],    
    packages = ['objbrowser', 'objbrowser.qtpy', 'objbrowser.qtpy._patch'],
    requires = ['six'])
    #packages = find_packages()) # requires the enduser to install setuptools
