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

        self._size = None
        self.__parse_size(storage_volume_item)
        self._storage_pool = None
        self.__parse_storage_pool(storage_volume_item)
        self._format = None
        self.__parse_format(storage_volume_item)

    def __parse_size(self, conf):
        """
            Parses the size parameter over the conf dictionary given in
            parameter and raises appropriate exception if a problem is found.
        """
        if not conf.has_key('size'):
            raise CloubedConfigurationException(
                      "size parameter of storage volume {name} is missing" \
                          .format(name=self._name))

        size = conf['size']

        if type(size) is not int:
            raise CloubedConfigurationException(
                      "format of size parameter of storage volume {name} is " \
                      "not valid".format(name=self._name))

        self._size = size

    def __parse_storage_pool(self, conf):
        """
            Parses the storage pool parameter over the conf dictionary given in
            parameter and raises appropriate exception if a problem is found.
        """
        if not conf.has_key('storagepool'):
            raise CloubedConfigurationException(
                      "storagepool parameter of storage volume {name} is " \
                      "missing".format(name=self._name))

        storage_pool = conf['storagepool']

        if type(storage_pool) is not str:
            raise CloubedConfigurationException(
                      "format of storagepool parameter of storage volume " \
                      "{name} is not valid".format(name=self._name))

        self._storage_pool = storage_pool

    def __parse_format(self, conf):
        """
            Parses the format parameter over the conf dictionary given in
            parameter and raises appropriate exception if a problem is found.
        """
        if conf.has_key('format'):

            vol_format = conf['format']

            if type(vol_format) is not str:
                raise CloubedConfigurationException(
                          "format of format parameter of storage volume " \
                          "{name} is not valid".format(name=self._name))

            valid_vol_formats = [ 'qcow2', 'raw' ]

            if vol_format not in valid_vol_formats:
                raise CloubedConfigurationException(
                          "value of format parameter of storage volume " \
                          "{name} is not valid".format(name=self._name))

            self._format = vol_format

        else:
            # default value to qcow2
            self._format = 'qcow2'

    def _get_type(self):

        """ Returns the type of the item """

        return u"storage volume"

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
                     .format(name=clean_name) : str(self._format),
                 "storagevolume.{name}.size"        \
                     .format(name=clean_name) : str(self._size),
                 "storagevolume.{name}.storagepool" \
                     .format(name=clean_name) : str(self._storage_pool) }
