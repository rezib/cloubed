#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright 2013-2020 Rémi Palancher
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

from cloubed.conf.ConfigurationItem import ConfigurationItem
from cloubed.CloubedException import CloubedConfigurationException

class ConfigurationStorageVolume(ConfigurationItem):

    """ Storage Volume Configuration class """

    def __init__(self, conf, storage_volume_item):

        super(ConfigurationStorageVolume, self).__init__(conf, storage_volume_item)

        self.size = None
        self.__parse_size(storage_volume_item)
        self.storage_pool = None
        self.__parse_storage_pool(storage_volume_item)
        self.format = None
        self.__parse_format(storage_volume_item)
        self.backing = None
        self.__parse_backing(storage_volume_item)

    def __parse_size(self, conf):
        """
            Parses the size parameter over the conf dictionary given in
            parameter and raises appropriate exception if a problem is found.
        """
        if 'size' not in conf:
            raise CloubedConfigurationException(
                      "size parameter of storage volume {name} is missing" \
                          .format(name=self.name))

        size = conf['size']

        if type(size) is not int:
            raise CloubedConfigurationException(
                      "format of size parameter of storage volume {name} is " \
                      "not valid".format(name=self.name))

        self.size = size

    def __parse_storage_pool(self, conf):
        """
            Parses the storage pool parameter over the conf dictionary given in
            parameter and raises appropriate exception if a problem is found.
        """
        if 'storagepool' not in conf:
            # if only storage, pop it for this storage volume volume
            if len(self.conf.storage_pools) == 1:
                self.storage_pool = self.conf.storage_pools[0].name
            else:
                raise CloubedConfigurationException(
                      "storagepool parameter of storage volume {name} is " \
                      "missing".format(name=self.name))

        else:
            storage_pool = conf['storagepool']

            if type(storage_pool) is not str:
                raise CloubedConfigurationException(
                      "format of storagepool parameter of storage volume " \
                      "{name} is not valid".format(name=self.name))

            self.storage_pool = storage_pool

    def __parse_format(self, conf):
        """
            Parses the format parameter over the conf dictionary given in
            parameter and raises appropriate exception if a problem is found.
        """
        if 'format' in conf:

            vol_format = conf['format']

            if type(vol_format) is not str:
                raise CloubedConfigurationException(
                          "format of format parameter of storage volume " \
                          "{name} is not valid".format(name=self.name))

            valid_vol_formats = [ 'qcow2', 'raw' ]

            if vol_format not in valid_vol_formats:
                raise CloubedConfigurationException(
                          "value of format parameter of storage volume " \
                          "{name} is not valid".format(name=self.name))

            self.format = vol_format

        else:
            # default value to qcow2
            self.format = 'qcow2'

    def __parse_backing(self, conf):
        """
            Parses the backing parameter over the conf dictionary given in
            parameter and raises appropriate exception if a problem is found.
        """
        if 'backing' in conf:

            # TODO: is size parameter useless in this case? TBC.

            backing = conf['backing']

            if type(backing) is not str:
                raise CloubedConfigurationException(
                          "format of backing parameter of storage volume " \
                          "{name} is not valid".format(name=self.name))

            self.backing = backing

        else:
            # default to None, aka. no backing
            self.backing = None

    def _get_type(self):

        """ Returns the type of the item """

        return "storage volume"
