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

""" ConfigurationNetwork class """

import logging
import os
from ..CloubedException import CloubedConfigurationException

class ConfigurationNetwork:

    """ Network Configuration class """

    def __init__(self, network_item):

        self._name = network_item['name']
        self._testbed = network_item['testbed']

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

    def get_testbed(self):

        """ Returns the name of the testbed """

        return self._testbed

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
