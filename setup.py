#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='python-digg',
    version='1.2',
    description='Python interface to the Digg API',
    author='Jeremy Grosser',
    author_email='synack@digg.com',
    packages=['digg'],
    install_requires=['oauth2>=1.2.0',
                      'simplejson'],
    extras_require={'memcache': ['python-memcached>=1.45']}
    )
