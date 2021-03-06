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

""" ConfigurationStoragePool class """

import os
from cloubed.conf.ConfigurationItem import ConfigurationItem
from cloubed.CloubedException import CloubedConfigurationException

class ConfigurationStoragePool(ConfigurationItem):

    """ Configuration of Storage Pool class """

    def __init__(self, conf, storage_pool_item):

        super(ConfigurationStoragePool, self).__init__(conf, storage_pool_item)

        self.path = None
        self.__parse_path(storage_pool_item)

    @staticmethod
    def default():
        return { 'name': 'pool',
                 'path': 'pool' }

    def __parse_path(self, conf):
        """
            Parses the path parameter over the conf dictionary given in
            parameter and raises appropriate exception if a problem is found
        """

        if 'path' not in conf:
            raise CloubedConfigurationException(
                      "path parameter is missing on storage pool {name}" \
                      .format(name=self.name))

        path = conf['path']

        if type(path) is not str:
            raise CloubedConfigurationException(
                     "format of the path parameter on storage pool {name} is " \
                     "not valid".format(name=self.name))

        self.path = conf['path']

        # handle relative path
        if self.path[0] != '/':
            self.path = os.path.join(os.getcwd(), self.path)

    def _get_type(self):

        """ Returns the type of the item """

        return "storage pool"