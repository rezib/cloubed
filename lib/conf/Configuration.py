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

""" Configuration class """

import logging
from ..CloubedException import CloubedConfigurationException
from ConfigurationLoader import ConfigurationLoader
from ConfigurationStoragePool import ConfigurationStoragePool
from ConfigurationStorageVolume import ConfigurationStorageVolume
from ConfigurationNetwork import ConfigurationNetwork
from ConfigurationDomain import ConfigurationDomain

class Configuration:

    """ Main Configuration class """

    def __init__(self, conf_file):

        self._file_path = conf_file
        self._loader = ConfigurationLoader(conf_file)
        self._conf = self._loader.get_content()

        self._check_main_keys(["storagepools",
                               "storagevolumes",
                               "networks",
                               "domains"])

        self._storage_pools_list = []
        for storage_pool_item in self._conf['storagepools']:
            storage_pool_item['testbed'] = self._conf['testbed']
            self._storage_pools_list \
                .append(ConfigurationStoragePool(storage_pool_item))

        self._storage_volumes_list = []
        for storage_volume_item in self._conf['storagevolumes']:
            storage_volume_item['testbed'] = self._conf['testbed']
            self._storage_volumes_list \
                .append(ConfigurationStorageVolume(storage_volume_item))

        self._networks_list = []
        for network_item in self._conf['networks']:
            network_item['testbed'] = self._conf['testbed']
            self._networks_list \
                .append(ConfigurationNetwork(network_item))

        self._domains_list = []
        for domain_item in self._conf['domains']:
            domain_item['testbed'] = self._conf['testbed']
            self._domains_list \
                .append(ConfigurationDomain(domain_item))

    def _check_main_keys(self, keys_list):

        """ checks conf dict contains all keys in keys_list """

        for key in keys_list:
            if not self._conf.has_key(key):
                raise CloubedConfigurationException(
                          "File {file_path} does not contain {key}" \
                              .format(file_path=self._file_path,
                                      key=key))

    def get_file_path(self):

        """ get_file_path: Returns the absolute path of the configuration file """

        return self._file_path

    def get_testbed_name(self):

        """ Returns the name of the testbed """

        return self._conf['testbed']

    def get_storage_pools_list(self):

        """ Returns the list of storage pools configurations """

        return self._storage_pools_list

    def get_storage_volumes_list(self):

        """ Returns the list of storage volumes configurations """

        return self._storage_volumes_list

    def get_networks_list(self):

        """ Returns the list of networks configurations """

        return self._networks_list

    def get_domains_list(self):

        """ Returns the list of domains configurations """

        return self._domains_list

    def get_templates_dict(self):

        """ Returns a dictionary with all parameters in configuration file """

        result_dict = { 'testbed': self.get_testbed_name() }

        for storage_pool in self.get_storage_pools_list():
            result_dict.update(storage_pool.get_templates_dict())
        for storage_volume in self.get_storage_volumes_list():
            result_dict.update(storage_volume.get_templates_dict())
        for network in self.get_networks_list():
            result_dict.update(network.get_templates_dict())
        for domain in self.get_domains_list():
            result_dict.update(domain.get_templates_dict())

        return result_dict
