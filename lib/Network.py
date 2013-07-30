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

""" Network class of Cloubed """

import logging
from xml.dom.minidom import Document

class Network:

    """ Network class """

    _networks = [] 

    def __init__(self, conn, network_conf):

        self._conn = conn
        self._virtobj = None

        self._name = network_conf.get_name()

        self._with_nat = network_conf.get_nat()

        self._with_local_settings = False
        self._ip_host = None
        self._netmask = None
        if network_conf.has_local_settings():
            self._with_local_settings = True
            self._ip_host = network_conf.get_ip_host()
            self._netmask = network_conf.get_netmask()

        self._with_dhcp = False
        self._dhcp_range_start = None
        self._dhcp_range_stop = None
        if network_conf.has_dhcp():
            self._with_dhcp = True
            self._dhcp_range_start = network_conf.get_dhcp_start()
            self._dhcp_range_end = network_conf.get_dhcp_end()

        self._with_pxe = False
        self._tftproot = None
        self._bootfile = None
        if network_conf.has_pxe():
            self._with_pxe = True
            self._tftproot = network_conf.get_pxe_tftp_dir()
            self._bootfile = network_conf.get_pxe_boot_file()

        Network._networks.append(self)

        self._doc = None
        self.__init_xml()

    def __del__(self):

        Network._networks.remove(self)

    def __eq__(self, other): # needed for __del__

        return self._name == other.get_name()

    @classmethod
    def get_network_list(cls):

        """ get_network_list: Returns the list of Networks """

        return cls._networks

    @classmethod
    def get_by_name(cls, network_name):

        """ get_by_name: Returns the Network with name given in parameter """

        for network in cls._networks:
            if network.get_name() == network_name:
                return network

        return None

    def toxml(self):

        """ toxml: Returns the libvirt XML representation of the Network """

        return self._doc.toxml()

    def getvirtobj(self):

        """ getvirtobj: Returns the libvirt object of the Network """

        return self._virtobj

    def get_name(self):

        """ get_name: Returns the name of the network """

        return self._name

    def created(self):

        """ created: Returns True if Network is created in libvirt """

        return self._virtobj is not None

    def create(self, overwrite = False):

        """ create: Creates the Network in libvirt """

        if overwrite:
            for network_name in self._conn.listDefinedNetworks():
                if network_name == self._name:
                    network = self._conn.networkLookupByName(network_name)
                    logging.info("undefining network " + network_name)
                    network.undefine()
            for network_name in self._conn.listNetworks():
                if network_name == self._name:
                    network = self._conn.networkLookupByName(network_name)
                    logging.info("destroying network " + network_name)
                    network.destroy()
            self._virtobj = self._conn.networkCreateXML(self.toxml())
        else:
            if self._name in self._conn.listNetworks():
                self._virtobj = self._conn.networkLookupByName(self._name)
            else:
                self._virtobj = self._conn.networkCreateXML(self.toxml())

    def __init_xml(self):

        """
            __init_xml: Generates the libvirt XML representation of the Network
        """

        self._doc = Document()

        # Open vSwitch - not used yet in libvirt 0.9.10

        # <network>
        #   <name>ovs-network</name>
        #   <forward mode='bridge'/>
        #   <bridge name='ovsbr0' />
        #   <virtualport type='openvswitch'/>
        #   <portgroup name='green' default='yes'>
        #     <virtualport>
        #       <parameters profileid='green-profile'/>
        #     </virtualport>
        #   </portgroup>
        #   <portgroup name='blue'>
        #     <vlan>
        #       <tag id='2'/>
        #     </vlan>
        #     <virtualport>
        #       <parameters profileid='blue-profile'/>
        #     </virtualport>
        #   </portgroup>
        # </network>

        # Isolated network

        # <network>
        #   <name>private</name>
        #   <bridge name="virbr2" />
        #   <forward mode="nat"/>
        #   <ip address="192.168.152.1" netmask="255.255.255.0">
        #     <tftp root="/var/lib/tftp" />
        #     <dhcp>
        #       <range start="192.168.152.20" end="192.168.152.254" />
        #       <bootp file='filename' />
        #     </dhcp>
        #   </ip>
        # </network>

        # root element: network
        element_network = self._doc.createElement("network")
        self._doc.appendChild(element_network)

        # name element
        element_name = self._doc.createElement("name")
        node_name = self._doc.createTextNode(self._name)
        element_name.appendChild(node_name)
        element_network.appendChild(element_name)
        
        # bridge element
        element_bridge = self._doc.createElement("bridge")
        #element_bridge.setAttribute("name","virbr2")
        element_network.appendChild(element_bridge)

        # forward element
        if self._with_nat:
            element_forward = self._doc.createElement("forward")
            element_forward.setAttribute("mode", "nat")
            element_network.appendChild(element_forward)
        
        # ip element
        if self._with_local_settings:
            element_ip = self._doc.createElement("ip")
            element_ip.setAttribute("address", self._ip_host)
            element_ip.setAttribute("netmask", self._netmask)
            element_network.appendChild(element_ip)

        # ip/tftp element
        if self._with_pxe:
            element_tftp = self._doc.createElement("tftp")
            element_tftp.setAttribute("root", self._tftproot)
            element_ip.appendChild(element_tftp)

        if self._with_dhcp:
            # ip/dhcp element
            element_dhcp = self._doc.createElement("dhcp")
            element_ip.appendChild(element_dhcp)
    
            # ip/dhcp/range element
            element_range = self._doc.createElement("range")
            element_range.setAttribute("start", self._dhcp_range_start)
            element_range.setAttribute("end", self._dhcp_range_end)
            element_dhcp.appendChild(element_range)
    
            # ip/dhcp/bootp
            if self._with_pxe:
                element_bootp = self._doc.createElement("bootp")
                element_bootp.setAttribute("file", self._bootfile)
                element_dhcp.appendChild(element_bootp)
