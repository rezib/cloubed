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

import logging
from Utils import gen_mac

class DomainNetif:

    """ DomainNetif class """

    def __init__(self, tbd, hostname, netif_conf):

        self.network = tbd.get_network_by_name(netif_conf["network"])
        if netif_conf.has_key("mac"):
            self.mac = netif_conf["mac"]
        else:
            self.mac = gen_mac("{domain:s}-{network:s}" \
                                  .format(domain=hostname,
                                          network=self.network.name))
            logging.debug("generated mac {mac} for netif on domain {domain} "\
                          "connected to network {network}" \
                              .format(mac=self.mac,
                                      domain=hostname,
                                      network=self.network.name))
        self.ip = netif_conf.get('ip')
        if self.ip is not None:
            self.network.register_host(hostname, self.mac, self.ip)

    def get_network_name(self):

        """
            Returns the name of the Network connected to the domain interface
        """

        return self.network.name


