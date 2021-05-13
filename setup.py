#!/usr/bin/env python
# -*- coding: utf-8 -*-

# To make a release type:
#   rm -rf build dist
#   python setup.py sdist --formats=zip

# Then upload to PiPy with
#   twine check dist/*
#   twine upload dist/objbrowser-1.2.0.zip

from objbrowser.version import DEBUGGING, PROGRAM_VERSION
from setuptools import setup

assert not DEBUGGING, "DEBUGGING must be False"

setup(name = 'objbrowser',
    version = PROGRAM_VERSION, 
    description = 'GUI for Python object introspection.',
    long_description = open('README.txt').read(),
    long_description_content_type = 'text/x-rst',
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
    packages = ['objbrowser'],
    install_requires = ['six', 'qtpy'])
