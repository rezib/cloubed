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


""" DomainNetif class of Cloubed """

from Network import Network

class DomainNetif:

    """ DomainNetif class """

    def __init__(self, hostname, mac, ip, network):

        self._hostname = hostname
        self._mac = mac
        self._ip = ip
        self._network = Network.get_by_name(network)
        if self._ip is not None:
            self._network.register_host(hostname, mac, ip)

    def get_mac(self):

        """ get_mac: Returns the MAC address of the domain interface """

        return self._mac

    def get_network(self):

        """
            get_network: Returns the Network connected to the domain interface
        """

        return self._network

    def get_network_name(self):

        """
            Returns the name of the Network connected to the domain interface
        """

        return self._network.get_name()


