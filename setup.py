#!/usr/bin/env python

from os.path import exists
from setuptools import setup
import metafunc

setup(
    name='metafunc',
    version=metafunc.__version__,
    description='TODO',
    url='http://github.com/eriknw/metafunc/',
    author='https://raw.github.com/eriknw/metafunc/master/AUTHORS.md',
    maintainer='Erik Welch',
    maintainer_email='erik.n.welch@gmail.com',
    license='BSD',
    keywords='TODO',
    packages=[
        'metafunc',
    ],
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Scientific/Engineering',
    ],
    long_description=open('README.md').read() if exists("README.md") else "",
    zip_safe=False,
)
