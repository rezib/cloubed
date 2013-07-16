#!/usr/bin/env python

from distutils.core import setup

setup(name='Cloubed',
      version='0.1',
      description='Utility and library to easily setup virtual testbeds composed of several KVM virtual machines through libvirt',
      author='Rémi Palancher',
      author_email='remi@rezib.org',
      package_dir = {'cloubed': 'lib'},
      packages=['cloubed'],
     )
