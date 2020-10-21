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

""" Configuration class """

import logging
from cloubed.CloubedException import CloubedConfigurationException
from cloubed.conf.ConfigurationStoragePool import ConfigurationStoragePool
from cloubed.conf.ConfigurationStorageVolume import ConfigurationStorageVolume
from cloubed.conf.ConfigurationNetwork import ConfigurationNetwork
from cloubed.conf.ConfigurationDomain import ConfigurationDomain

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

        self.templates = {} # empty dict
        self.__parse_templates(conf)

    def __parse_testbed(self, conf):
        """
            Parses the testbed parameter over the conf dictionary given in
            parameter and raises appropriate exception if a problem is found
        """

        if 'testbed' not in conf:
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

        optional_items = [ 'storagepools', 'storagevolumes' ]

        # Iterations over the dict. The variables are:
        #   item_section: the name of the section in YAML
        #   meta: the dict with 'class' and 'list' for the section
        #   items: the list of items in the section
        #   item_class: the ConfigurationItem class for the items
        #   item_list: the list to append with build ConfigurationItem objects

        for item_section, meta in list(items.items()):

            item_class = meta['class']
            item_list = meta['list']

            if item_section not in conf:
                if item_section in optional_items:
                    logging.debug("loading defaut {item_section}" \
                                  .format(item_section=item_section))
                    default_item = item_class.default()
                    if default_item is not None:
                        item_list.append(item_class(self, default_item))
                else:
                    raise CloubedConfigurationException(
                          "{item_section} parameter is missing" \
                              .format(item_section=item_section))
            else:
                items = conf[item_section]
                if type(items) is not list:
                    raise CloubedConfigurationException(
                          "format of {item_section} parameter is not valid" \
                             .format(item_section=item_section))

                for item in items:
                    item['testbed'] = self.testbed
                    item_list.append(item_class(self, item))

    def __parse_templates(self, conf):
        """
            Parses the global testbed template variables in the dedicated
            section of the conf dictionary given in parameter and raises
            appropriate exception if a problem is found
        """

        if "templates" in conf:

            templates = conf["templates"]

            if type(templates) is not dict:
                raise CloubedConfigurationException(
                    "format of the templates section is not valid")

            if len(templates) == 0:
                self.templates = {}
            else:
                for variable, value in list(templates.items()):
                    if type(value) is not str:
                        raise CloubedConfigurationException(
                            "format of the value of the global template " \
                            "variable {variable} is not valid" \
                                .format(variable=variable))
                    key = "testbed.{variable}".format(variable=variable)
                    self.templates[key] = value
        else:
            # empty dict by default
            self.templates = {}