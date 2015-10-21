#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages
from mvnupdate.mvnupdate import __version__

setup(
    name='mvn-update',
    version=__version__,
    packages=find_packages(),
    url='https://victorhqggqvsit.com',
    license='MIT',
    author='Victor Häggqvist',
    author_email='victor@hggqvst.com',
    description='Maven artifact version updater',
    entry_points={
        'console_scripts': ['mvn-update=mvnupdate.mvnupdate:main']
    },
    download_url="https://github.com/victorhaggqvist/mvn-update/tarball/0.2.1"
)
