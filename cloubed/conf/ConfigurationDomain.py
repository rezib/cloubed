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

""" ConfigurationDomain class """

import re
import os
from cloubed.conf.ConfigurationItem import ConfigurationItem
from cloubed.conf.ConfigurationStorageVolume import ConfigurationStorageVolume
from cloubed.VirtController import VirtController
from cloubed.CloubedException import CloubedConfigurationException

class ConfigurationDomain(ConfigurationItem):

    """ Domain Configuration class """

    def __init__(self, conf, domain_item):

        super(ConfigurationDomain, self).__init__(conf, domain_item)

        self.sockets = None
        self.cores = None
        self.threads = None

        self.__parse_cpu(domain_item)
        self.memory = None
        self.__parse_memory(domain_item)
        self.graphics = None
        self.__parse_graphics(domain_item)

        self.netifs = []
        self.__parse_netifs(domain_item)

        self.disks = []
        self.__parse_disks(domain_item)

        self.cdrom = None
        self.__parse_cdrom(domain_item)

        self.virtfs = []
        self.__parse_virtfs(domain_item)

        self.template_files = []
        self.template_vars = {}
        self.__parse_templates(domain_item)

    def __parse_cpu(self, conf):
        """
            Parses the cpu parameter over the conf dictionary given in parameter
            and raises appropriate exception if a problem is found.
        """

        if 'cpu' not in conf:
            raise CloubedConfigurationException(
                       "cpu parameter of domain {domain} is missing" \
                           .format(domain=self.name))

        cpu = conf['cpu']

        if type(cpu) is int:
            self.sockets = 1
            self.cores = cpu
            self.threads = 1
        elif type(cpu) is str:
            cpu_topo = cpu.split('x')
            if len(cpu_topo) != 3:
                raise CloubedConfigurationException(
                           "format of cpu topology of domain {domain} is " \
                           "not valid".format(domain=self.name))
            for elem in cpu_topo:
                if not elem.isdigit():
                    raise CloubedConfigurationException(
                           "format of cpu topology of domain {domain} is " \
                           "not valid".format(domain=self.name))

            self.sockets = int(cpu_topo[0])
            self.cores = int(cpu_topo[1])
            self.threads = int(cpu_topo[2])
        else:
            raise CloubedConfigurationException(
                       "format of cpu parameter of domain {domain} is not " \
                       "valid".format(domain=self.name))

    def __parse_memory(self, conf):
        """
            Parses the memory parameter over the conf dictionary given in
            parameter and raises appropriate exception if a problem is found.
        """

        if 'memory' not in conf:
            raise CloubedConfigurationException(
                       "memory parameter of domain {domain} is missing" \
                           .format(domain=self.name))

        multiplier = 1024 # default unit in YAML is GiB
                          # but Cloubed internally stores memory size in MiB

        memory = conf['memory']

        if type(memory) is int:
            qty = memory
        elif type(memory) is str:

            pattern = re.compile("(\d+)\s*(\w*)")
            match = pattern.match(memory)

            if match is None:
                raise CloubedConfigurationException(
                          "memory size '{memory}' of domain {domain} is not " \
                          "valid" \
                              .format(memory=memory,
                                      domain=self.name))

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
                                      domain=self.name))
        else:
            raise CloubedConfigurationException(
                       "format of memory parameter of domain {domain} is not " \
                       "valid" \
                           .format(memory=memory,
                                   domain=self.name))

        self.memory = multiplier * qty

    def __parse_graphics(self, conf):
        """
            Parses the graphics parameter over the conf dictionary given in
            parameter and raises appropriate exception if a problem is found.
        """

        if 'graphics' in conf:

            graphics = conf['graphics']

            if type(graphics) is not str:
                raise CloubedConfigurationException(
                          "format of graphics parameter of domain {domain} " \
                          "is not valid" \
                              .format(domain=self.name))

            valid_graphics = ["sdl", "vnc", "rdp", "spice"]

            if graphics not in valid_graphics:
                raise CloubedConfigurationException(
                          "value {graphics} of graphics parameter of domain " \
                          "{domain} is not valid" \
                              .format(graphics=graphics,
                                      domain=self.name))

            self.graphics = graphics

        else:
            # default is spice if controller has support
            if VirtController.supports_spice():
                self.graphics = "spice"
            else:
                self.graphics = "vnc"

    def __parse_netifs(self, conf):
        """
            Parses the netifs section of parameters over the conf dictionary
            given in parameter and raises appropriate exception if a problem is
            found.
        """

        if 'netifs' not in conf:
            raise CloubedConfigurationException(
                      "netifs section of domain {domain} is missing" \
                          .format(domain=self.name))

        netifs = conf['netifs']

        if type(netifs) is not list:
            raise CloubedConfigurationException(
                      "format of netifs section of domain {domain} is not " \
                      "valid".format(domain=self.name))

        netif_id = 0

        for netif in netifs:

            if type(netif) is not dict:
                raise CloubedConfigurationException(
                          "format of netif {netif_id} of domain {domain} is " \
                          "not valid" \
                              .format(netif_id=netif_id,
                                      domain=self.name))


            if "network" not in netif:
                raise CloubedConfigurationException(
                          "network of netif {netif_id} of domain {domain} is " \
                          "missing" \
                              .format(netif_id=netif_id,
                                      domain=self.name))

            if type(netif["network"]) is not str:
                raise CloubedConfigurationException(
                          "format of network of netif {netif_id} of domain "\
                          "{domain} is not valid" \
                              .format(netif_id=netif_id,
                                      domain=self.name))

            if "ip" in netif and \
               type(netif["ip"]) is not str:
                raise CloubedConfigurationException(
                          "format of ip of netif {netif_id} of domain "\
                          "{domain} is not valid" \
                              .format(netif_id=netif_id,
                                      domain=self.name))

            if "mac" in netif:

                if type(netif["mac"]) is not str:
                    raise CloubedConfigurationException(
                              "format of mac of netif {netif_id} of domain "\
                              "{domain} is not valid" \
                                  .format(netif_id=netif_id,
                                          domain=self.name))

                # check mac against this regexp
                mac_regexp = r"^([0-9a-fA-F]{2}:){5}([0-9a-fA-F]{2})$"

                if re.match(mac_regexp, netif["mac"]) is None:
                    raise CloubedConfigurationException(
                              "value of mac parameter of netif {netif_id} of " \
                              "domain {domain} is not a valid mac address" \
                                  .format(netif_id=netif_id,
                                          domain=self.name))

            self.netifs.append(netif)

            netif_id += 1

    def __parse_disks(self, conf):
        """
            Parses the disks section of parameters over the conf dictionary
            given in parameter and raises appropriate exception if a problem is
            found.
        """

        self.disks = []

        if 'disks' not in conf:
            raise CloubedConfigurationException(
                      "disks section of domain {domain} is missing" \
                          .format(domain=self.name))

        disks = conf['disks']

        if type(disks) is not list:
            raise CloubedConfigurationException(
                      "format of disks section of domain {domain} is not " \
                      "valid".format(domain=self.name))

        disk_id = 0

        for disk in disks:

            if type(disk) is not dict:
                raise CloubedConfigurationException(
                          "format of disk {disk_id} of domain {domain} is " \
                          "not valid" \
                              .format(disk_id=disk_id,
                                      domain=self.name))


            if "device" not in disk:
                raise CloubedConfigurationException(
                          "device of disk {disk_id} of domain {domain} " \
                          "is missing" \
                              .format(disk_id=disk_id,
                                      domain=self.name))

            if type(disk["device"]) is not str:
                raise CloubedConfigurationException(
                          "format of device of disk {disk_id} of domain " \
                          "{domain} is not valid" \
                              .format(disk_id=disk_id,
                                      domain=self.name))

            if "bus" in disk:
                bus = disk["bus"]
                if type(bus) is not str:
                    raise CloubedConfigurationException(
                              "format of bus of disk {disk_id} of domain " \
                              "{domain} is not valid" \
                                  .format(disk_id=disk_id,
                                          domain=self.name))

                valid_buses = ["virtio", "scsi", "ide"]

                if bus not in valid_buses:
                    raise CloubedConfigurationException(
                              "value {bus} of bus of disk {disk_id} of " \
                              "domain {domain} is not valid" \
                                  .format(bus=bus,
                                          disk_id=disk_id,
                                          domain=self.name))

            else:

                # default value
                disk["bus"] = "virtio"

            if "storage_volume" in disk and "name" in disk:
                raise CloubedConfigurationException(
                          "storage_volume and name parameters of disk " \
                          "{disk_id} of domain {domain} are conflicting" \
                              .format(disk_id=disk_id,
                                      domain=self.name))

            if "storage_volume" in disk:

                if type(disk["storage_volume"]) is not str:
                    raise CloubedConfigurationException(
                              "format of storage_volume parameter of disk " \
                              "{disk_id} of domain {domain} is not valid" \
                                  .format(disk_id=disk_id,
                                          domain=self.name))


            elif "name" in disk:

                sp_item = disk.copy()
                sp_params = [ 'name', 'storagepool', 'size', 'format', 'backing' ]
                for key in list(sp_item.keys()):
                    if key not in sp_params:
                        del sp_item[key]

                sp = ConfigurationStorageVolume(self.conf, sp_item)
                self.conf.storage_volumes.append(sp)

                disk['storage_volume'] = sp.name

            else:
                raise CloubedConfigurationException(
                          "storage_volume or name parameters of disk " \
                          "{disk_id} of domain {domain} are missing" \
                              .format(disk_id=disk_id,
                                      domain=self.name))


            self.disks.append(disk)

            disk_id += 1

    def __parse_cdrom(self, conf):
        """
            Parses the cdrom parameter over the conf dictionary given in
            parameter and raises appropriate exception if a problem is found.
        """

        self.cdrom = None

        if 'cdrom' in conf:

            cdrom = conf['cdrom']

            if type(cdrom) is not str:
                raise CloubedConfigurationException(
                          "format of cdrom parameter of domain {domain} " \
                          "is not valid" \
                              .format(domain=self.name))

            # handle relative path
            if cdrom[0] != '/':
                cdrom = os.path.join(os.getcwd(), cdrom)

            self.cdrom = cdrom

    def __parse_virtfs(self, conf):
        """
            Parses the virtfs section of parameters over the conf dictionary
            given in parameter and raises appropriate exception if a problem is
            found.
        """

        self.virtfs = []

        if 'virtfs' in conf:

            virtfs = conf['virtfs']

            if type(virtfs) is not list:
                raise CloubedConfigurationException(
                          "format of virtfs section of domain {domain} is " \
                          "not valid".format(domain=self.name))

            id = 0

            for fs in virtfs:

                if type(fs) is not dict:
                    raise CloubedConfigurationException(
                              "format of virtfs {id} of domain {domain} is " \
                              "not valid" \
                                  .format(id=id, domain=self.name))

                if "source" not in fs:
                    raise CloubedConfigurationException(
                              "source of virtfs {id} of domain {domain} is " \
                              "missing" \
                                  .format(id=id, domain=self.name))

                if type(fs["source"]) is not str:
                    raise CloubedConfigurationException(
                              "format of source of virtfs {id} of domain " \
                              "{domain} is not valid" \
                                  .format(id=id, domain=self.name))

                source = fs["source"]

                # handle relative source path
                if source[0] != '/':
                    source = os.path.join(os.getcwd(), source)

                if "target" in fs and type(fs["target"]) is not str:
                    raise CloubedConfigurationException(
                              "format of target of virtfs {id} of domain " \
                              "{domain} is not valid" \
                                  .format(id=id, domain=self.name))

                if "target" in fs:
                    target = fs["target"]
                else:
                    target = source # default target is equal to source

                self.virtfs.append({"source": source, "target": target})

            id += 1

    def __parse_templates(self, conf):
        """
            Call parsers for both files and variables parameters defined in the
            dedicated section of the dictionary given in parameter. If the
            optional section is not defined, set attributes to default empty
            dict value.
        """

        if 'templates' in conf:
            self.__parse_templates_files(conf['templates'])
            self.__parse_templates_vars(conf['templates'])
        else:
            self.template_files = []
            self.template_vars = {}

    def __parse_templates_files(self, conf):
        """
            Parses all the template files parameters over the conf dictionary
            given in parameter and raises appropriate exception if a problem is
            found.
        """
        if 'files' in conf:
            tpl_files = conf['files']
            # files section must be a list a dict with keys name, input and
            # output
            if type(tpl_files) is not list:
                raise CloubedConfigurationException(
                    "format of the files sub-section in the templates " \
                    "section of domain {domain} templates is not valid" \
                        .format(domain = self.name))

            for tpl_file in tpl_files:

                required_parameters = ['name', 'input', 'output']
                for parameter in required_parameters:
                    if parameter not in tpl_file:
                        raise CloubedConfigurationException(
                            "{parameter} parameter of a template file of " \
                            "domain {domain} is missing" \
                                .format(parameter = parameter,
                                        domain = self.name))
                    if type(tpl_file[parameter]) is not str:
                        raise CloubedConfigurationException(
                            "format of {parameter} parameter of a template " \
                            "file of domain {domain} is not valid" \
                                .format(parameter = parameter,
                                        domain = self.name))
                # everything is clear at this point
                self.template_files.append(tpl_file)
        else:
            self.template_files = []

    def __parse_templates_vars(self, conf):
        """
            Parses all the template variables over the conf dictionary given in
            parameter and raises appropriate exception if a problem is found.
        """
        if 'vars' in conf:
            tpl_vars = conf['vars']
            # vars section must be a dict of {string,(string/int) pairs
            if type(tpl_vars) is not dict:
                raise CloubedConfigurationException(
                    "format of the vars sub-section in the templates " \
                    "section of domain {domain} templates is not valid" \
                        .format(domain = self.name))

            for key, value in list(tpl_vars.items()):
                if type(value) is not str and type(value) is not int:
                    raise CloubedConfigurationException(
                          "format of the value of {key} template variable of " \
                          "domain {domain} is not valid"
                                .format(key = key,
                                        domain = self.name))
                # everything is clear at this point
                self.template_vars[key] = str(value)
        else:
            self.template_vars = {}

    def _get_type(self):

        """ Returns the type of the item """

        return "domain"