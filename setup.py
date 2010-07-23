#!/usr/bin/env python
import os
import re

try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension


if os.path.isfile('MANIFEST'):
    os.unlink('MANIFEST')


version = re.search('__version__ = "([^"]+)"',
                    open('ooop.py').read()).group(1)

setup(
    name = 'ooop',
    version = version,
    description = 'OpenObject on Python, a library to connect with Open ERP.',
    author = 'Pedro Gracia',
    author_email = 'lasarux@neuroomante.com',
    license = 'GPLv3+',
    download_url = 'https://www.github.com/lasarux/ooop',
    py_modules = ['ooop'],
    #package_dir = {'ooop': 'src/'},
    #packages = ['ooop'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Python Software Foundation License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
