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

        # forward
        self._forward_mode = None
        self.__parse_forward_mode(network_item)

        # bridge name
        self._bridge_name = None
        self.__parse_bridge_name(network_item)

        # local settings
        self._ip_host = None
        self._netmask = None

        if network_item.has_key('ip_host') and network_item.has_key('netmask'):
            self._ip_host = network_item['ip_host']
            self._netmask = network_item['netmask']

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

    def __parse_forward_mode(self, conf):
        """
            Parses the forward parameter over the conf dictionary given in
            parameter and raises appropriate exception if a problem is found.
        """

        if conf.has_key('forward'):

            forward = conf['forward']

            if type(forward) is str:

                valid_forwards = ["bridge", "nat", "none"]

                if forward in valid_forwards:
                    if forward == "none":
                        self._forward_mode = None
                    else:
                        self._forward_mode = forward
                else:
                    raise CloubedConfigurationException(
                        "Forward parameter of network {network} is not valid" \
                            .format(network=self._name))

            else:
                raise CloubedConfigurationException(
                    "Forward parameter format of network {network} is not " \
                    "valid".format(network=self._name))

        else:

            self._forward_mode = None # default value if not defined

    def __parse_bridge_name(self, conf):
        """
            Parses the bridge parameter over the conf dictionary given in
            parameter and raises appropriate exception if a problem is found.
            This method must be called *after* __parse_forward_mode() since
            it relies on attributes set by this method.
        """

        # forward is not bridge -> bridge parameter has no sense
        if self._forward_mode is not 'bridge' and conf.has_key('bridge'):
             raise CloubedConfigurationException(
                 "Bridge parameter has no sense on network {network} with " \
                 "forward mode {forward}" \
                     .format(network = self._name,
                             forward = self._forward_mode))

        # forward is bridge -> bridge parameter is mandatory
        elif self._forward_mode is 'bridge':

            if conf.has_key('bridge'):

                bridge = conf['bridge']
                if type(bridge) is str:
                    self._bridge_name = bridge
                else:
                    raise CloubedConfigurationException(
                        "Bridge parameter format of network {network} is not " \
                        "valid".format(network = self._name))

            else:
                raise CloubedConfigurationException(
                    "Bridge parameter is missing on network {network} with " \
                    "bridge forward mode" \
                        .format(network = self._name))

        else:
            # not bridge forward mode and bridge parameter not defined
            self._bridge_name = None

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

    def get_forward_mode(self):

        """ Returns the forward mode parameter in Network Configuration """

        return self._forward_mode

    def get_bridge_name(self):

        """ Returns the bridge name parameter in Network Configuration """

        return self._bridge_name

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

        return { "network.{name}.forward_mode" \
                     .format(name=clean_name) : self._forward_mode,
                 "network.{name}.bridge_name" \
                     .format(name=clean_name) : self._bridge_name,
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
