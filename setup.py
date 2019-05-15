#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

with open('PacteClient/version.py') as f:
    exec(f.read())

REQUIREMENTS = [
    "requests",
    "validators"
]

setup(name='PyPacteClient',
      version= __version__,
      author='Pierre-André Ménard',
      author_email='pierre-andre.menard@crim.ca',
      packages=find_packages(),
      install_requires=REQUIREMENTS,
      )
