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
from ..CloubedException import CloubedConfigurationException

class ConfigurationDomain:

    """ Domain Configuration class """

    def __init__(self, domain_item):

        self._name = domain_item['name']
        self._testbed = domain_item['testbed']
        self.__parse_cpu(domain_item['cpu'])
        self.__parse_memory(domain_item['memory'])
        self.__parse_graphics(domain_item['graphics'])

        self._netifs = []
        self.__parse_netifs(domain_item['netifs'])

        self._disks = {}
        self.__parse_disks(domain_item['disks'])

        if domain_item.has_key('templates'):
            if domain_item['templates'].has_key('files'):
                self._template_files = domain_item['templates']['files']
            else:
                self._template_files = {}
            if domain_item['templates'].has_key('vars'):
                self._template_vars = domain_item['templates']['vars']
            else:
                self._template_vars = {}
        else:
            self._template_files = {}
            self._template_vars = {}

    def __parse_cpu(self, cpu):

        if type(cpu) is not int:
            raise CloubedConfigurationException(
                       "CPU '{cpu}' of domain {domain} is not valid, please " \
                       "see documentation.".format(cpu=cpu, domain=self._name))
        self._cpu = int(cpu)

    def __parse_memory(self, memory):

        multiplier = 1024 # default unit in YAML is GiB
                          # but Cloubed internally stores memory size in MiB
        memory_qty = -1
        if type(memory) is int:
            qty = memory
        elif type(memory) is str:

            pattern = re.compile(u"(\d+)\s*(\w*)")
            match = pattern.match(memory)

            if match is None:
                raise CloubedConfigurationException(
                          "Memory size '{memory}' of domain {domain} is not " \
                          "valid, please see documentation." \
                              .format(memory=memory,
                                      domain=self._name))

            qty = int(match.group(1))
            unit = match.group(2)

            if unit in ["M", "MB", "MiB"]:
                multiplier = 1
            elif unit in ["G", "GB", "GiB"]:
                multiplier = 1024
            else:
                raise CloubedConfigurationException("Unknown unit for memory" \
                          " '{memory}' of domain {domain}" \
                              .format(memory=memory,
                                      domain=self._name))
        else: # invalid type
            raise CloubedConfigurationException(
                       "Memory size '{memory}' of domain {domain} is not " \
                       "valid, please see documentation." \
                           .format(memory=memory,
                                   domain=self._name))

        self._memory = multiplier * qty

    def __parse_graphics(self, graphics):

        if type(graphics) is str:

            valid_graphics = ["sdl", "vnc", "rdp", "spice"]

            if graphics in valid_graphics:
                self._graphics = graphics

            else: # invalid choice
                raise CloubedConfigurationException(
                          "Graphics '{graphics}' of domain {domain} is not " \
                          "valid." \
                              .format(graphics=graphics,
                                      domain=self._name))

        else: # invalid type
            raise CloubedConfigurationException(
                      "Graphics of domain {domain} has not a valid format." \
                          .format(domain=self._name))

    def __parse_netifs(self, netifs):

        if type(netifs) is list:

            netif_id = 0

            for netif in netifs:

                if type(netif) is not dict:
                    raise CloubedConfigurationException(
                              "Netif {netif_id} of domain {domain} has not a " \
                              "valid format." \
                                  .format(netif_id=netif_id,
                                          domain=self._name))


                if not netif.has_key("network"):
                    raise CloubedConfigurationException(
                              "Netif {netif_id} of domain {domain} shoud have " \
                              "a network name." \
                                  .format(netif_id=netif_id,
                                          domain=self._name))

                if type(netif["network"]) is not str:
                    raise CloubedConfigurationException(
                              "Network name of netif {netif_id} of domain "\
                              "{domain} has not a valid format." \
                                  .format(netif_id=netif_id,
                                          domain=self._name))

                if netif.has_key("ip") and \
                   type(netif["ip"]) is not str:
                    raise CloubedConfigurationException(
                              "Network IP of netif {netif_id} of domain "\
                              "{domain} has not a valid format." \
                                  .format(netif_id=netif_id,
                                          domain=self._name))

                self._netifs.append(netif)

                netif_id += 1

        else: # invalid type
            raise CloubedConfigurationException(
                      "Netifs of domain {domain} has not a valid format." \
                          .format(domain=self._name))

    def __parse_disks(self, disks):

        if type(disks) is list:

            disk_id = 0

            for disk in disks:

                if type(disk) is not dict:
                    raise CloubedConfigurationException(
                              "disk {disk_id} of domain {domain} has not a " \
                              "valid format" \
                                  .format(disk_id=disk_id,
                                          domain=self._name))


                if not disk.has_key("device"):
                    raise CloubedConfigurationException(
                              "device is missing for disk {disk_id} of " \
                              "domain {domain}" \
                                  .format(disk_id=disk_id,
                                          domain=self._name))

                if not disk.has_key("storage_volume"):
                    raise CloubedConfigurationException(
                              "storage volume is missing for disk {disk_id} " \
                              "of domain {domain}" \
                                  .format(disk_id=disk_id,
                                          domain=self._name))


                if type(disk["device"]) is not str:
                    raise CloubedConfigurationException(
                              "device of disk {disk_id} of domain {domain} " \
                              "has not a valid format" \
                                  .format(disk_id=disk_id,
                                          domain=self._name))

                if type(disk["storage_volume"]) is not str:
                    raise CloubedConfigurationException(
                              "storage volume of disk {disk_id} of domain " \
                              "{domain} has not a valid format" \
                                  .format(disk_id=disk_id,
                                          domain=self._name))

                self._disks[disk["device"]] = disk["storage_volume"]

                disk_id += 1

        else: # invalid type
            raise CloubedConfigurationException(
                      "disks of domain {domain} has not a valid format" \
                          .format(domain=self._name))


    def get_name(self):

        """ Returns the name of the Domain in its Configuration """

        return self._name

    def get_testbed(self):

        """ Returns the name of the testbed """

        return self._testbed

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

    def get_templates_dict(self):

        """
            Returns a dictionary with all parameters of the Domain Configuration
        """

        clean_name = self._name.replace('-','')

        domain_dict = { "domain.{name}.cpu" \
                            .format(name=clean_name) : self._cpu,
                        "domain.{name}.memory" \
                            .format(name=clean_name) : self._memory,
                        "domain.{name}.graphics" \
                            .format(name=clean_name) : self._graphics,
                      }

        # add netifs
        for netif in self._netifs:
            if netif.has_key("ip"):
                key = "domain.{name}.{network}.ip" \
                          .format(name=clean_name,
                                  network=netif["network"])
                domain_dict[key] = netif["ip"]

        tpl_vars_dict = {}

        for var_key, var_value in self._template_vars.items():
            full_key = "domain.{name}.tpl.{var_name}" \
                           .format(name=clean_name, var_name=var_key)
            tpl_vars_dict[full_key] = var_value

        domain_dict.update(tpl_vars_dict)

        return domain_dict
