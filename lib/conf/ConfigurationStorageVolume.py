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

""" ConfigurationStorageVolume class """

from ConfigurationItem import ConfigurationItem
from ..CloubedException import CloubedConfigurationException

class ConfigurationStorageVolume(ConfigurationItem):

    """ Storage Volume Configuration class """

    def __init__(self, storage_volume_item):

        super(ConfigurationStorageVolume, self).__init__(storage_volume_item)

        self._format = storage_volume_item['format']
        self._size = storage_volume_item['size']
        self._storage_pool = storage_volume_item['storagepool']

    def get_format(self):

        """ Returns the format of the Storage Volume in Configuration """

        return self._format

    def get_size(self):

        """ Returns the size of the Storage Volume in Configuration """

        return self._size

    def get_storage_pool(self):

        """ Returns the name of associated Storage Pool in Configuration """

        return self._storage_pool

    def get_templates_dict(self):

        """
            Returns a dictionary with all parameters of the Storage Volume in
            Configuration
        """

        clean_name = ConfigurationItem.clean_string_for_template(self._name)

        return { "storagevolume.{name}.format"      \
                     .format(name=clean_name) : self._format,
                 "storagevolume.{name}.size"        \
                     .format(name=clean_name) : self._size,
                 "storagevolume.{name}.storagepool" \
                     .format(name=clean_name) : self._storage_pool }
