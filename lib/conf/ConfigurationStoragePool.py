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

""" ConfigurationStoragePool class """

import os
from ..CloubedException import CloubedConfigurationException

class ConfigurationStoragePool:

    """ Configuration of Storage Pool class """

    def __init__(self, storage_pool_item):

        self._name = storage_pool_item['name']
        self._testbed = storage_pool_item['testbed']
        self._path = storage_pool_item['path']

        if self._path[0] != '/': # relative path
            self._path = os.path.join(os.getcwd(), self._path)

    def get_name(self):

        """ Returns the name of the Storage Pool """

        return self._name

    def get_testbed(self):

        """ Returns the name of the testbed """

        return self._testbed

    def get_path(self):

        """ Returns the path of the Storage Pool """

        return self._path

    def get_templates_dict(self):

        """ Returns a dictionary with all parameters for the Storage Pool """

        clean_name = self._name.replace('-','')

        return { "storagepool.{name}.path" \
                     .format(name=clean_name) : self._path }
