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

""" Configuration classes"""

import yaml
import logging
import os
from CloubedException import CloubedException

class Configuration:

    """ Main Configuration class """

    def __init__(self, conf_file):

        self._file_path = conf_file

        try:
            yaml_file = open(self._file_path)
        except IOError:
            raise CloubedException("Not able to open file {file_path}" \
                                      .format(file_path = self._file_path))

        self._yaml = yaml.load(yaml_file)
        yaml_file.close()

        self._storage_pools_list = []
        for storage_pool_item in self._yaml['storagepools']:
            self._storage_pools_list \
                .append(ConfigurationStoragePool(storage_pool_item))

        self._storage_volumes_list = []
        for storage_volume_item in self._yaml['storagevolumes']:
            self._storage_volumes_list \
                .append(ConfigurationStorageVolume(storage_volume_item))

        self._networks_list = []
        for network_item in self._yaml['networks']:
            self._networks_list \
                .append(ConfigurationNetwork(network_item))

        self._domains_list = []
        for domain_item in self._yaml['domains']:
            self._domains_list \
                .append(ConfigurationDomain(domain_item))

    def get_file_path(self):

        """ get_file_path: Returns the absolute path of the configuration file """

        return self._file_path

    def get_testbed_name(self):

        """ Returns the name of the testbed """

        return self._yaml['testbed']

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

class ConfigurationStoragePool:

    """ Configuration of Storage Pool class """

    def __init__(self, storage_pool_item):

        self._name = storage_pool_item['name']

        self._path = storage_pool_item['path']

        if self._path[0] != '/': # relative path
            self._path = os.path.join(os.getcwd(), self._path)

    def get_name(self):

        """ Returns the name of the Storage Pool """

        return self._name

    def get_path(self):

        """ Returns the path of the Storage Pool """

        return self._path

    def get_templates_dict(self):

        """ Returns a dictionary with all parameters for the Storage Pool """

        clean_name = self._name.replace('-','')

        return { "storagepool.{name}.path" \
                     .format(name=clean_name) : self._path }

class ConfigurationStorageVolume:

    """ Storage Volume Configuration class """

    def __init__(self, storage_volume_item):

        self._name = storage_volume_item['name']
        self._format = storage_volume_item['format']
        self._size = storage_volume_item['size']
        self._storage_pool = storage_volume_item['storagepool']

    def get_name(self):

        """ Returns the name of the Storage Volume in Configuration """

        return self._name

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

        clean_name = self._name.replace('-','')

        return { "storagevolume.{name}.format"      \
                     .format(name=clean_name) : self._format,
                 "storagevolume.{name}.size"        \
                     .format(name=clean_name) : self._size,
                 "storagevolume.{name}.storagepool" \
                     .format(name=clean_name) : self._storage_pool }

class ConfigurationNetwork:

    """ Network Configuration class """

    def __init__(self, network_item):

        self._name = network_item['name']

        # nat
        self._nat = False
        if network_item.has_key('nat'):
            self._nat = network_item['nat']
       
        # local settings
        self._ip_host = None
        self._netmask = None

        if network_item.has_key('ip_host') and network_item.has_key('netmask'):
            self._ip_host = network_item['ip_host']
            self._netmask = network_item['netmask']
        else:
            logging.warning("no local settings defined for network {:s}" \
                                .format(self._name))

        # dhcp parameters
        self._dhcp_start = None
        self._dhcp_end = None

        # pxe parameters
        self._pxe_tftp_dir = None
        self._pxe_boot_file = None

        if network_item.has_key('dhcp') and \
           network_item['dhcp'].has_key('start') and \
           network_item['dhcp'].has_key('end'):
            self._dhcp_start = network_item['dhcp']['start']
            self._dhcp_end = network_item['dhcp']['end']

            # pxe depends on dhcp
            if network_item.has_key('pxe') and \
               network_item['pxe'].has_key('tftp_dir') and \
               network_item['pxe'].has_key('boot_file'):

                self._pxe_tftp_dir = network_item['pxe']['tftp_dir']
                if self._pxe_tftp_dir[0] != '/': # relative path
                    self._pxe_tftp_dir = os.path.join(os.getcwd(),
                                                      self._pxe_tftp_dir)
                

                self._pxe_boot_file = network_item['pxe']['boot_file']

            else:
                logging.warning("no pxe settings defined for network {:s}" \
                                    .format(self._name))

        else:
            logging.warning("no dhcp parameters defined for network {:s}" \
                                .format(self._name))

    def has_local_settings(self):

        """
            Returns True if Network Configuration has parameters for local
            settings, False otherwise.
        """

        return (self._ip_host is not None
                and self._netmask is not None)

    def has_dhcp(self):

        """
            Returns True if Network Configuration has parameters for DHCP
            server, False otherwise.
        """

        return (self._dhcp_start is not None
                and self._dhcp_end is not None)

    def has_pxe(self):

        """
            Returns True if Network Configuration has parameters for PXE server,
            False otherwise.
        """

        return (self._pxe_tftp_dir is not None
                and self._pxe_boot_file is not None)

    def get_name(self):

        """ Returns the name of the Network in the Configuration """

        return self._name

    def get_nat(self):

        """ Returns the nat parameter in Network Configuration """

        return self._nat

    def get_ip_host(self):

        """ Returns the IP of host in Network Configuration """

        return self._ip_host

    def get_netmask(self):

        """ Returns the netmask in Network Configuration """

        return self._netmask

    def get_dhcp_start(self):

        """
            Returns the start of IP addresses range for DHCP server in this
            Network Configuration
        """

        return self._dhcp_start

    def get_dhcp_end(self):

        """
            Returns the end of IP addresses range for DHCP server in this
            Network Configuration
        """

        return self._dhcp_end

    def get_pxe_tftp_dir(self):

        """
            Returns the root directory of the TFTP server in this Network
            Configuration
        """

        return self._pxe_tftp_dir

    def get_pxe_boot_file(self):

        """ Returns the boot file for PXE in this Network Configuration """

        return self._pxe_boot_file

    def get_templates_dict(self):

        """
            Returns a dictionary with all parameters of this Network
            Configuration
        """

        clean_name = self._name.replace('-','')

        return { "network.{name}.nat" \
                     .format(name=clean_name) : self._nat,
                 "network.{name}.ip_host" \
                     .format(name=clean_name) : self._ip_host,
                 "network.{name}.netmask" \
                     .format(name=clean_name) : self._netmask,
                 "network.{name}.dhcp_start" \
                     .format(name=clean_name) : self._dhcp_start,
                 "network.{name}.dhcp_end" \
                     .format(name=clean_name) : self._dhcp_end,
                 "network.{name}.pxe_tftp_dir" \
                     .format(name=clean_name) : self._pxe_tftp_dir,
                 "network.{name}.pxe_boot_file" \
                     .format(name=clean_name) : self._pxe_boot_file }

class ConfigurationDomain:

    """ Domain Configuration class """

    def __init__(self, domain_item):

        self._name = domain_item['name']
        self._cpu = int(domain_item['cpu'])
        self._memory = int(domain_item['memory'])
        self._graphics = domain_item['graphics']
        self._netifs = domain_item['netifs']
        self._disks = domain_item['disks']
        if domain_item.has_key('templates'):
            self._template_files = domain_item['templates']['files']
            self._template_vars = domain_item['templates']['vars']
        else:
            self._template_files = {}
            self._template_vars = {}

    def get_name(self):

        """ Returns the name of the Domain in its Configuration """

        return self._name

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

        disks_dict = {}
        for disk in self._disks:
            disks_dict[disk['device']] = disk['storage_volume']

        return disks_dict

    def get_templates_list(self):

        """ Returns the list of Templates of the Domain Configuration """

        return self._template_files

    def get_netifs_list(self):

        """
            Returns the list of network interfaces configurations of the Domain
            Configuration
        """

        return [ netif['network'] for netif in self._netifs ]

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
        tpl_vars_dict = {}

        for var_key, var_value in self._template_vars.items():
            full_key = "domain.{name}.tpl.{var_name}" \
                           .format(name=clean_name, var_name=var_key)
            tpl_vars_dict[full_key] = var_value

        domain_dict.update(tpl_vars_dict)

        return domain_dict
