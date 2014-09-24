#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013 Rémi Palancher
#
# This file is part of Cloubed.
#
# Cloubed is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# Cloubed is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with Cloubed.  If not, see
# <http://www.gnu.org/licenses/>.

from setuptools import setup

setup(name='cloubed',
      version='0.4',
      description='Utility and library to easily setup virtual testbeds composed of several KVM virtual machines through libvirt',
      author='Rémi Palancher',
      author_email='remi@rezib.org',
      package_dir={'cloubed': 'lib'},
      packages=['cloubed',
                'cloubed.cli',
                'cloubed.conf'],
      scripts=['scripts/cloubed'],
      install_requires=['argparse',
                        'pyyaml',
                        'libvirt-python',
                        'netaddr'],
      license='LGPLv3',
      url='http://cloubed.org/',
      platforms=['GNU/Linux']
     )
