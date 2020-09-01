#!/usr/bin/python3
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

import os
import re
import logging
from cloubed.conf.ConfigurationItem import ConfigurationItem
from cloubed.CloubedException import CloubedConfigurationException

class ConfigurationNetwork(ConfigurationItem):

    """ Network Configuration class """

    def __init__(self, conf, network_item):

        super(ConfigurationNetwork, self).__init__(conf, network_item)

        # forward
        self.forward_mode = None
        self.__parse_forward_mode(network_item)

        # bridge name
        self.bridge_name = None
        self.__parse_bridge_name(network_item)

        # local settings
        self.ip_host = None
        self.netmask = None
        self.__parse_ip_host_netmask(network_item)

        # dhcp parameters
        self.dhcp_start = None
        self.dhcp_end = None
        self.__parse_dhcp(network_item)

        # domain name
        self.domain = None
        self.__parse_domain(network_item)

        # pxe parameters
        self.pxe_tftp_dir = None
        self.pxe_boot_file = None
        self.__parse_pxe(network_item)

    def __parse_forward_mode(self, conf):
        """
            Parses the forward parameter over the conf dictionary given in
            parameter and raises appropriate exception if a problem is found.
        """

        if 'forward' in conf:

            forward = conf['forward']

            if type(forward) is str:

                valid_forwards = ["bridge", "nat", "none"]

                if forward in valid_forwards:
                    if forward == "none":
                        self.forward_mode = None
                    else:
                        self.forward_mode = forward
                else:
                    raise CloubedConfigurationException(
                        "Forward parameter of network {network} is not valid" \
                            .format(network=self.name))

            else:
                raise CloubedConfigurationException(
                    "Forward parameter format of network {network} is not " \
                    "valid".format(network=self.name))

        else:

            self.forward_mode = None # default value if not defined

    def __parse_bridge_name(self, conf):
        """
            Parses the bridge parameter over the conf dictionary given in
            parameter and raises appropriate exception if a problem is found.
            This method must be called *after* __parse_forward_mode() since
            it relies on the attribute set by this method.
        """

        # forward is not bridge -> bridge parameter has no sense
        if self.forward_mode != 'bridge' and 'bridge' in conf:
            raise CloubedConfigurationException(
                "Bridge parameter has no sense on network {network} with " \
                "forwarding mode {forward}" \
                    .format(network = self.name,
                            forward = self.forward_mode))

        # forward is bridge -> bridge parameter is mandatory
        elif self.forward_mode == 'bridge':

            if 'bridge' in conf:

                bridge = conf['bridge']
                if type(bridge) is str:
                    self.bridge_name = bridge
                else:
                    raise CloubedConfigurationException(
                        "Bridge parameter format of network {network} is not " \
                        "valid".format(network = self.name))

            else:
                raise CloubedConfigurationException(
                    "Bridge parameter is missing on network {network} with " \
                    "bridge forwarding mode" \
                        .format(network = self.name))

        else:
            # not bridge forward mode and bridge parameter not defined
            self.bridge_name = None

    def __parse_ip_host_netmask(self, conf):
        """
            Parses the address or deprecated (ip_host and netmask) parameters
            over the conf dictionary given in parameter and raises appropriate
            exception if a problem is found. This method must be called *after*
            __parse_forward_mode() since it relies on the attribute set by this
           method.
        """

        # forward is bridge -> address has no sense
        if self.forward_mode == 'bridge' and 'address' in conf :
            raise CloubedConfigurationException(
                "address parameter has no sense on network {network} with " \
                "bridge forwarding mode".format(network=self.name))

        # forward is bridge -> ip_host and netmask have no sense
        if self.forward_mode == 'bridge' and \
           ( 'ip_host' in conf or 'netmask' in conf ):
            raise CloubedConfigurationException(
                "ip_host and netmask parameters have no sense on network " \
                "{network} with bridge forwarding mode" \
                    .format(network=self.name))

        if 'address' in conf:

            address = conf['address']

            if type(address) is not str:
                raise CloubedConfigurationException(
                        "address parameter format on network {network} is " \
                        "not valid".format(network=self.name))

            try:
                from netaddr import IPNetwork, AddrFormatError
            except ImportError:
                raise CloubedConfigurationException(
                        "unable to parse address parameter on network " \
                        "{network} because netaddr module is not available" \
                        .format(network=self.name))
            try:
                network = IPNetwork(address)
            except AddrFormatError:
                raise CloubedConfigurationException(
                        "address parameter on network {network} is not a " \
                        "valid network address".format(network=self.name))

            self.ip_host = str(network.ip)
            self.netmask = str(network.netmask)

        # ip_host needs netmask
        elif 'ip_host' in conf and 'netmask' not in conf:
            raise CloubedConfigurationException(
                "ip_host cannot be set without netmask parameter on network " \
                "{network}".format(network=self.name))

        # netmask needs ip_host
        elif 'netmask' in conf and 'ip_host' not in conf:
            raise CloubedConfigurationException(
                "netmask cannot be set without ip_host parameter on network " \
                "{network}".format(network=self.name))

        elif 'ip_host' in conf and 'netmask' in conf:

            logging.warning("ip_host/netmask network parameters are " \
                            "deprecated, please use address parameter instead")

            ip_host = conf['ip_host']
            netmask = conf['netmask']

            # check type of values
            if type(ip_host) is not str:
                raise CloubedConfigurationException(
                    "ip_host parameter format on network {network} is not " \
                    "valid".format(network=self.name))
            if type(netmask) is not str:
                raise CloubedConfigurationException(
                    "netmask parameter format on network {network} is not " \
                    "valid".format(network=self.name))

            # check parameters against this regexp
            ip_address_regexp = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"

            if re.match(ip_address_regexp, ip_host) is None:
                raise CloubedConfigurationException(
                    "ip_host parameter on network {network} is not a valid " \
                    "IPv4 address".format(network=self.name))

            if re.match(ip_address_regexp, netmask) is None:
                raise CloubedConfigurationException(
                    "netmask parameter on network {network} is not a valid " \
                    "IPv4 netmask".format(network=self.name))

            # at this point, everything is clear
            self.ip_host = ip_host
            self.netmask = netmask

        else:
            # attributes default to None
            self.ip_host = None
            self.netmask = None

    def __parse_dhcp(self, conf):
        """
            Parses the dhcp parameters over the conf dictionary given in
            parameter and raises appropriate exception if a problem is found.
            This method must be called *after* __parse_ip_host_netmask() since
            it relies on the attributes set by this method.
        """

        # dhcp cannot be set-up on networks in bridge forwarding mode but it is
        # useless to test it here since it is actually a recursive dependency
        # with the ip_host

        # dhcp cannot be set-up without ip_host/netmask
        if self.ip_host is None and 'dhcp' in conf:
            raise CloubedConfigurationException(
                "dhcp service cannot be set-up on network {network} without " \
                "ip_host and netmask".format(network = self.name))

        if 'dhcp' in conf:

            dhcp_conf = conf['dhcp']

            dhcp_parameters = ['start', 'end']

            # check parameters against this regexp
            ip_address_regexp = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"

            for parameter in dhcp_parameters:

                if parameter not in dhcp_conf:
                    raise CloubedConfigurationException(
                        "{parameter} parameter must be defined in dhcp " \
                        "section of network {network}" \
                            .format(parameter = parameter,
                                    network = self.name))

                if type(dhcp_conf[parameter]) is not str:
                    raise CloubedConfigurationException(
                        "{parameter} parameter format in dhcp section of " \
                        "network {network} is not valid" \
                            .format(parameter = parameter,
                                    network = self.name))

                if re.match(ip_address_regexp, dhcp_conf[parameter]) is None:
                    raise CloubedConfigurationException(
                        "{parameter} parameter in dhcp section of network " \
                        "{network} is not a valid IPv4 address" \
                            .format(parameter = parameter,
                                    network = self.name))

            # everything is clear at this point
            self.dhcp_start = dhcp_conf['start']
            self.dhcp_end = dhcp_conf['end']

        else:
            # default to None if not defined
            self.dhcp_start = None
            self.dhcp_end = None

    def __parse_domain(self, conf):
        """
            Parses the domain parameter over the conf dictionary given in
            parameter and raises appropriate exception if a problem is found.
            This method must be called *after* __parse_dhcp() since
            it relies on the attributes set by this method.
        """

        # domain cannot be set-up without dhcp
        if self.dhcp_start is None and 'domain' in conf:
            raise CloubedConfigurationException(
                "domain parameter cannot be set-up on network {network} " \
                "without dhcp".format(network = self.name))

        if 'domain' in conf:

            domain = conf['domain']

            if type(domain) is not str:
                raise CloubedConfigurationException(
                    "format of domain parameter of network {network} is not " \
                    "valid".format(network = self.name))

            self.domain = domain

        else:
            # default is None
            self.domain = None

    def __parse_pxe(self, conf):
        """
            Parses the pxe parameters over the conf dictionary given in
            parameter and raises appropriate exception if a problem is found.
            This method must be called *after* __parse_dhcp() since
            it relies on the attributes set by this method.
        """

        # pxe cannot be set-up without dhcp
        if self.dhcp_start is None and 'pxe' in conf:
            raise CloubedConfigurationException(
                "pxe service cannot be set-up on network {network} without " \
                "dhcp".format(network = self.name))

        if 'pxe' in conf:

            pxe_conf = conf['pxe']

            if type(pxe_conf) is str:
                (self.pxe_tftp_dir, self.pxe_boot_file) = os.path.split(pxe_conf)

                if self.pxe_tftp_dir == '':
                    self.pxe_tftp_dir = os.getcwd()
                if self.pxe_boot_file == '':
                    raise CloubedConfigurationException(
                        "pxe parameter of network {network} must specify " \
                        "a boot file".format(network=self.name))

            elif type(pxe_conf) is dict:

                logging.warning("pxe parameter format with tftp_dir and " \
                                "boot_file parameters is deprecated")

                pxe_parameters = ['tftp_dir', 'boot_file']

                # check that all parameters are present and valid strings
                for parameter in pxe_parameters:

                    if parameter not in pxe_conf:
                        raise CloubedConfigurationException(
                            "{parameter} parameter must be defined in pxe " \
                            "section of network {network}" \
                                .format(parameter=parameter,
                                        network=self.name))

                    if type(pxe_conf[parameter]) is not str:
                        raise CloubedConfigurationException(
                            "{parameter} parameter format in pxe section of " \
                            "network {network} is not valid" \
                                .format(parameter=parameter,
                                        network=self.name))

                # everything is clear at this point
                self.pxe_tftp_dir = pxe_conf['tftp_dir']
                self.pxe_boot_file = pxe_conf['boot_file']

            else:
                raise CloubedConfigurationException(
                    "format of pxe parameter of network {network} is not " \
                    "valid".format(network=self.name))

            if self.pxe_tftp_dir[0] != '/': # relative path
                self.pxe_tftp_dir = os.path.join(os.getcwd(),
                                                 self.pxe_tftp_dir)

        else:
            # default to None if not defined
            self.pxe_tftp_dir = None
            self.pxe_boot_file = None

    def _get_type(self):

        """ Returns the type of the item """

        return "network"

    def has_local_settings(self):

        """
            Returns True if Network Configuration has parameters for local
            settings, False otherwise.
        """

        return (self.ip_host is not None
                and self.netmask is not None)

    def has_dhcp(self):

        """
            Returns True if Network Configuration has parameters for DHCP
            server, False otherwise.
        """

        return (self.dhcp_start is not None
                and self.dhcp_end is not None)

    def has_pxe(self):

        """
            Returns True if Network Configuration has parameters for PXE server,
            False otherwise.
        """

        return (self.pxe_tftp_dir is not None
                and self.pxe_boot_file is not None)

    def get_templates_dict(self):

        """
            Returns a dictionary with all parameters of this Network
            Configuration
        """

        clean_name = ConfigurationItem.clean_string_for_template(self.name)

        tpl_dict = { "network.{name}.forward_mode" \
                         .format(name=clean_name) : str(self.forward_mode),
                     "network.{name}.bridge_name" \
                         .format(name=clean_name) : str(self.bridge_name),
                     "network.{name}.ip_host" \
                         .format(name=clean_name) : str(self.ip_host),
                     "network.{name}.netmask" \
                         .format(name=clean_name) : str(self.netmask),
                     "network.{name}.dhcp_start" \
                         .format(name=clean_name) : str(self.dhcp_start),
                     "network.{name}.dhcp_end" \
                         .format(name=clean_name) : str(self.dhcp_end),
                     "network.{name}.pxe_tftp_dir" \
                         .format(name=clean_name) : str(self.pxe_tftp_dir),
                     "network.{name}.pxe_boot_file" \
                         .format(name=clean_name) : str(self.pxe_boot_file) }

        # port is hard-coded in HTTPServer class
        if self.ip_host is not None:
            http_server = "http://" + self.ip_host + ":5432"
            tpl_dict["network.{name}.http_server" \
                     .format(name=clean_name)] = http_server

        return tpl_dict
