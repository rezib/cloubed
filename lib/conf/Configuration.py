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
from ConfigurationStoragePool import ConfigurationStoragePool
from ConfigurationStorageVolume import ConfigurationStorageVolume
from ConfigurationNetwork import ConfigurationNetwork
from ConfigurationDomain import ConfigurationDomain

class Configuration:

    """ Main Configuration class """

    def __init__(self, loader):

        self._loader = loader
        conf = self._loader.content

        self.testbed = None
        self.__parse_testbed(conf)

        self.storage_pools   = []
        self.storage_volumes = []
        self.networks        = []
        self.domains         = []
        self.__parse_items(conf)

        self._templates = {} # empty dict
        self.__parse_templates(conf)

    def __parse_testbed(self, conf):
        """
            Parses the testbed parameter over the conf dictionary given in
            parameter and raises appropriate exception if a problem is found
        """

        if not conf.has_key('testbed'):
            raise CloubedConfigurationException(
                      "testbed parameter is missing")

        if type(conf['testbed']) is not str:
            raise CloubedConfigurationException(
                      "format of the testbed parameter is not valid")

        self.testbed = conf['testbed']

    def __parse_items(self, conf):
        """
            Parses all items (storage pools, storage volumes, networks and
            domains) over the conf dictionary given in parameter and raises
            appropriate exception if a problem is found
        """

        # This dict basically contains all infos to parse items in YAML and
        # build according data structures. The format of this dict is:
        # <name of section for the items in YAML> : {
        #        { 'class': <ConfigurationItem class for these items>,
        #          'list': <list to append with the Configuration object> }

        items = { 'storagepools':
                      { 'class': ConfigurationStoragePool,
                        'list': self.storage_pools },
                  'storagevolumes':
                      { 'class': ConfigurationStorageVolume,
                        'list': self.storage_volumes },
                  'networks':
                      { 'class': ConfigurationNetwork,
                        'list': self.networks },
                  'domains':
                      { 'class': ConfigurationDomain,
                        'list': self.domains } }

        # Iterations over the dict. The variables are:
        #   item_section: the name of the section in YAML
        #   meta: the dict with 'class' and 'list' for the section
        #   items: the list of items in the section
        #   item_class: the ConfigurationItem class for the items
        #   item_list: the list to append with build ConfigurationItem objects

        for item_section, meta in items.iteritems():
            if not conf.has_key(item_section):
                raise CloubedConfigurationException(
                          "{item_section} parameter is missing" \
                              .format(item_section=item_section))
            items = conf[item_section]
            if type(items) is not list:
                  raise CloubedConfigurationException(
                          "format of {item_section} parameter is not valid" \
                              .format(item_section=item_section))

            item_class = meta['class']
            item_list = meta['list']

            for item in items:
                item['testbed'] = self.testbed
                item_list.append(item_class(item))

    def __parse_templates(self, conf):
        """
            Parses the global testbed template variables in the dedicated
            section of the conf dictionary given in parameter and raises
            appropriate exception if a problem is found
        """

        if conf.has_key("templates"):

            templates = conf["templates"]

            if type(templates) is not dict:
                raise CloubedConfigurationException(
                    "format of the templates section is not valid")

            if len(templates) == 0:
                self._templates = {}
            else:
                for variable, value in templates.iteritems():
                    if type(value) is not str:
                        raise CloubedConfigurationException(
                            "format of the value of the global template " \
                            "variable {variable} is not valid" \
                                .format(variable=variable))
                    key = "testbed.{variable}".format(variable=variable)
                    self._templates[key] = value
        else:
            # empty dict by default
            self._templates = {}

    def get_templates_dict(self, domain_name):

        """ Returns a dictionary with all parameters in configuration file """

        result_dict = { 'testbed': self.testbed }

        result_dict.update(self._templates)

        for storage_pool in self.storage_pools:
            result_dict.update(storage_pool.get_templates_dict())
        for storage_volume in self.storage_volumes:
            result_dict.update(storage_volume.get_templates_dict())
        for network in self.networks:
            result_dict.update(network.get_templates_dict())
        for domain in self.domains:
            result_dict.update(domain.get_absolute_templates_dict())
            if domain.name == domain_name:
                result_dict.update(domain.get_contextual_templates_dict())

        return result_dict
