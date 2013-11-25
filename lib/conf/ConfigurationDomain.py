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

""" ConfigurationDomain class """

import re
from ConfigurationItem import ConfigurationItem
from ..CloubedException import CloubedConfigurationException

class ConfigurationDomain(ConfigurationItem):

    """ Domain Configuration class """

    def __init__(self, domain_item):

        super(ConfigurationDomain, self).__init__(domain_item)

        self._cpu = None
        self.__parse_cpu(domain_item)
        self._memory = None
        self.__parse_memory(domain_item)
        self._graphics = None
        self.__parse_graphics(domain_item)

        self._netifs = []
        self.__parse_netifs(domain_item)

        self._disks = {}
        self.__parse_disks(domain_item)

        self._template_files = []
        self._template_vars = {}
        self.__parse_templates(domain_item)

    def __parse_cpu(self, conf):
        """
            Parses the cpu parameter over the conf dictionary given in parameter
            and raises appropriate exception if a problem is found.
        """

        if not conf.has_key('cpu'):
            raise CloubedConfigurationException(
                       "cpu parameter of domain {domain} is missing" \
                           .format(domain=self._name))

        cpu = conf['cpu']

        if type(cpu) is not int:
            raise CloubedConfigurationException(
                       "format of cpu parameter of domain {domain} is not " \
                       "valid".format(domain=self._name))

        self._cpu = cpu

    def __parse_memory(self, conf):
        """
            Parses the memory parameter over the conf dictionary given in
            parameter and raises appropriate exception if a problem is found.
        """

        if not conf.has_key('memory'):
            raise CloubedConfigurationException(
                       "memory parameter of domain {domain} is missing" \
                           .format(domain=self._name))

        multiplier = 1024 # default unit in YAML is GiB
                          # but Cloubed internally stores memory size in MiB
        memory_qty = -1

        memory = conf['memory']

        if type(memory) is int:
            qty = memory
        elif type(memory) is str:

            pattern = re.compile(u"(\d+)\s*(\w*)")
            match = pattern.match(memory)

            if match is None:
                raise CloubedConfigurationException(
                          "memory size '{memory}' of domain {domain} is not " \
                          "valid" \
                              .format(memory=memory,
                                      domain=self._name))

            qty = int(match.group(1))
            unit = match.group(2)

            if unit in ["M", "MB", "MiB"]:
                multiplier = 1
            elif unit in ["G", "GB", "GiB"]:
                multiplier = 1024
            else:
                raise CloubedConfigurationException("unknown unit for memory" \
                          " '{memory}' of domain {domain}" \
                              .format(memory=memory,
                                      domain=self._name))
        else:
            raise CloubedConfigurationException(
                       "format of memory parameter of domain {domain} is not " \
                       "valid" \
                           .format(memory=memory,
                                   domain=self._name))

        self._memory = multiplier * qty

    def __parse_graphics(self, conf):
        """
            Parses the graphics parameter over the conf dictionary given in
            parameter and raises appropriate exception if a problem is found.
        """

        if conf.has_key('graphics'):

            graphics = conf['graphics']

            if type(graphics) is not str:
                raise CloubedConfigurationException(
                          "format of graphics parameter of domain {domain} " \
                          "is not valid" \
                              .format(domain=self._name))

            valid_graphics = ["sdl", "vnc", "rdp", "spice"]

            if graphics not in valid_graphics:
                raise CloubedConfigurationException(
                          "value {graphics} of graphics parameter of domain " \
                          "{domain} is not valid" \
                              .format(graphics=graphics,
                                      domain=self._name))

            self._graphics = graphics

        else:
            # default is spice
            self._graphics = "spice"

    def __parse_netifs(self, conf):
        """
            Parses the netifs section of parameters over the conf dictionary
            given in parameter and raises appropriate exception if a problem is
            found.
        """

        if not conf.has_key('netifs'):
            raise CloubedConfigurationException(
                      "netifs section of domain {domain} is missing" \
                          .format(domain=self._name))

        netifs = conf['netifs']

        if type(netifs) is not list:
            raise CloubedConfigurationException(
                      "format of netifs section of domain {domain} is not " \
                      "valid".format(domain=self._name))

        netif_id = 0

        for netif in netifs:

            if type(netif) is not dict:
                raise CloubedConfigurationException(
                          "format of netif {netif_id} of domain {domain} is " \
                          "not valid" \
                              .format(netif_id=netif_id,
                                      domain=self._name))


            if not netif.has_key("network"):
                raise CloubedConfigurationException(
                          "network of netif {netif_id} of domain {domain} is " \
                          "missing" \
                              .format(netif_id=netif_id,
                                      domain=self._name))

            if type(netif["network"]) is not str:
                raise CloubedConfigurationException(
                          "format of network of netif {netif_id} of domain "\
                          "{domain} is not valid" \
                              .format(netif_id=netif_id,
                                      domain=self._name))

            if netif.has_key("ip") and \
               type(netif["ip"]) is not str:
                raise CloubedConfigurationException(
                          "format of ip of netif {netif_id} of domain "\
                          "{domain} is not valid" \
                              .format(netif_id=netif_id,
                                      domain=self._name))

            self._netifs.append(netif)

            netif_id += 1

    def __parse_disks(self, conf):
        """
            Parses the disks section of parameters over the conf dictionary
            given in parameter and raises appropriate exception if a problem is
            found.
        """

        if not conf.has_key('disks'):
            raise CloubedConfigurationException(
                      "disks section of domain {domain} is missing" \
                          .format(domain=self._name))

        disks = conf['disks']

        if type(disks) is not list:
            raise CloubedConfigurationException(
                      "format of disks section of domain {domain} is not " \
                      "valid".format(domain=self._name))

        disk_id = 0

        for disk in disks:

            if type(disk) is not dict:
                raise CloubedConfigurationException(
                          "format of disk {disk_id} of domain {domain} is " \
                          "not valid" \
                              .format(disk_id=disk_id,
                                      domain=self._name))


            if not disk.has_key("device"):
                raise CloubedConfigurationException(
                          "device of disk {disk_id} of domain {domain} " \
                          "is missing" \
                              .format(disk_id=disk_id,
                                      domain=self._name))

            if not disk.has_key("storage_volume"):
                raise CloubedConfigurationException(
                          "storage volume of disk {disk_id} of domain " \
                          "{domain} is missing" \
                              .format(disk_id=disk_id,
                                      domain=self._name))


            if type(disk["device"]) is not str:
                raise CloubedConfigurationException(
                          "format of device of disk {disk_id} of domain " \
                          "{domain} is not valid" \
                              .format(disk_id=disk_id,
                                      domain=self._name))

            if type(disk["storage_volume"]) is not str:
                raise CloubedConfigurationException(
                          "format of storage volume of disk {disk_id} of " \
                          "domain {domain} is not valid" \
                              .format(disk_id=disk_id,
                                      domain=self._name))

            self._disks[disk["device"]] = disk["storage_volume"]

            disk_id += 1

    def __parse_templates(self, conf):
        """
            Call parsers for both files and variables parameters defined in the
            dedicated section of the dictionary given in parameter. If the
            optional section is not defined, set attributes to default empty
            dict value.
        """

        if conf.has_key('templates'):
            self.__parse_templates_files(conf['templates'])
            self.__parse_templates_vars(conf['templates'])
        else:
            self._template_files = []
            self._template_vars = {}

    def __parse_templates_files(self, conf):
        """
            Parses all the template files parameters over the conf dictionary
            given in parameter and raises appropriate exception if a problem is
            found.
        """
        if conf.has_key('files'):
            tpl_files = conf['files']
            # files section must be a list a dict with keys name, input and
            # output
            if type(tpl_files) is not list:
                raise CloubedConfigurationException(
                    "format of the files sub-section in the templates " \
                    "section of domain {domain} templates is not valid" \
                        .format(domain = self._name))

            for tpl_file in tpl_files:

                required_parameters = ['name', 'input', 'output']
                for parameter in required_parameters:
                    if not tpl_file.has_key(parameter):
                        raise CloubedConfigurationException(
                            "{parameter} parameter of a template file of " \
                            "domain {domain} is missing" \
                                .format(parameter = parameter,
                                        domain = self._name))
                    if type(tpl_file[parameter]) is not str:
                        raise CloubedConfigurationException(
                            "format of {parameter} parameter of a template " \
                            "file of domain {domain} is not valid" \
                                .format(parameter = parameter,
                                        domain = self._name))
                # everything is clear at this point
                self._template_files.append(tpl_file)
        else:
            self._template_files = []

    def __parse_templates_vars(self, conf):
        """
            Parses all the template variables over the conf dictionary given in
            parameter and raises appropriate exception if a problem is found.
        """
        if conf.has_key('vars'):
            tpl_vars = conf['vars']
            # vars section must be a dict of {string,(string/int) pairs
            if type(tpl_vars) is not dict:
                raise CloubedConfigurationException(
                    "format of the vars sub-section in the templates " \
                    "section of domain {domain} templates is not valid" \
                        .format(domain = self._name))

            for key, value in tpl_vars.iteritems():
                if type(value) is not str and type(value) is not int:
                    raise CloubedConfigurationException(
                          "format of the value of {key} template variable of " \
                          "domain {domain} is not valid"
                                .format(key = key,
                                        domain = self._name))
                # everything is clear at this point
                self._template_vars[key] = str(value)
        else:
            self._template_vars = {}

    def _get_type(self):

        """ Returns the type of the item """

        return u"domain"

    def get_cpu(self):

        """ Returns the number of CPU of the Domain Configuration """

        return self._cpu 

    def get_memory(self):

        """ Returns the memory size of the Domain Configuration """

        return self._memory

    def get_graphics(self):

        """ Returns graphics parameter of the Domain Configuration """

        return self._graphics

    def get_disks_dict(self):

        """
            Returns a dictionary of all parameters of all disks of the Domain
            Configuration
        """


        return self._disks

    def get_templates_list(self):

        """ Returns the list of Templates of the Domain Configuration """

        return self._template_files

    def get_netifs_list(self):

        """
            Returns the list of network interfaces configurations of the Domain
            Configuration
        """

        return self._netifs

    def get_contextual_templates_dict(self):

        """
            Returns a dictionary with all parameters of the Domain Configuration
            with contextual prefix
        """

        return self.get_templates_dict(prefix="self")

    def get_absolute_templates_dict(self):

        """
            Returns a dictionary with all parameters of the Domain Configuration
            with absolute prefix
        """

        clean_name = ConfigurationItem.clean_string_for_template(self._name)
        return self.get_templates_dict(prefix = \
                                       "domain.{name}".format(name=clean_name))

    def get_templates_dict(self, prefix):

        """
            Returns a dictionary with all parameters of the Domain Configuration
        """

        clean_name = ConfigurationItem.clean_string_for_template(self._name)
        domain_dict = { "{prefix}.name" \
                            .format(prefix=prefix) : str(clean_name),
                        "{prefix}.cpu" \
                            .format(prefix=prefix) : str(self._cpu),
                        "{prefix}.memory" \
                            .format(prefix=prefix) : str(self._memory),
                        "{prefix}.graphics" \
                            .format(prefix=prefix) : str(self._graphics),
                      }

        # add netifs
        for netif in self._netifs:
            if netif.has_key("ip"):
                network_clean_name = \
                    ConfigurationItem.clean_string_for_template(netif['network'])
                key = "{prefix}.{network}.ip" \
                          .format(prefix=prefix,
                                  network=network_clean_name)
                domain_dict[key] = str(netif["ip"])

        tpl_vars_dict = {}

        for var_key, var_value in self._template_vars.items():
            full_key = "{prefix}.tpl.{var_name}" \
                           .format(prefix=prefix, var_name=var_key)
            tpl_vars_dict[full_key] = str(var_value)

        domain_dict.update(tpl_vars_dict)

        return domain_dict
