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
from xml.dom.minidom import Document, parseString
from Utils import getuser

class Network:

    """ Network class """

    _networks = [] 

    def __init__(self, conn, network_conf):

        self._conn = conn
        self._virtobj = None

        self._name = network_conf.get_name()
        use_namespace = True # should better be a conf parameter in the future
        if use_namespace:    # logic should moved be in an abstract parent class
            self._libvirt_name = \
                "{user}:{testbed}:{name}" \
                    .format(user = getuser(),
                            testbed = network_conf.get_testbed(),
                            name = self._name)
        else:
            self._libvirt_name = self._name

        self._forward_mode = network_conf.get_forward_mode()
        self._bridge_name = network_conf.get_bridge_name()

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

        # list of statically declared hosts in the network
        self._hosts = []

        Network._networks.append(self)

        self._doc = None

    def __del__(self):

        try:
            Network._networks.remove(self)
        except ValueError:
            pass

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

    def xml(self):

        """ Returns the libvirt XML representation of the Network """

        self.__init_xml()
        return self._doc

    def toxml(self):

        """ Returns the libvirt XML representation of the Network as string """

        return self.xml().toxml()

    def getvirtobj(self):

        """ getvirtobj: Returns the libvirt object of the Network """

        return self._virtobj

    def find_network(self):

        networks = self._conn.listNetworks() + self._conn.listDefinedNetworks()
        for network_name in networks:

            if network_name == self._libvirt_name:

                return self._conn.networkLookupByName(network_name)

        return None

    def get_infos(self):
        """
            Returns a dict full of key/value string pairs with information about
            the Network
        """

        infos = {}

        network = self.find_network()
        if network is not None:

            # status name of the Network from Libvirt standpoint
            if network.isActive():
                infos['status'] = 'active'
            else:
                infos['status'] = 'inactive'

            # extract infos out of libvirt XML
            xml = parseString(network.XMLDesc(0))

            # IndexError exception is passed in order to continue silently
            # if elements are not found in the XML tree

            # bridge name
            try:
                element = xml.getElementsByTagName('bridge').pop()
                bridge = element.getAttribute('name')
                infos['bridge'] = bridge
            except IndexError:
                pass

            # current ip/netmask
            try:
                element = xml.getElementsByTagName('ip').pop()
                ip = element.getAttribute('address')
                infos['ip'] = ip
                netmask = element.getAttribute('netmask')
                infos['netmask'] = netmask
            except IndexError:
                pass

        else:
            infos['status'] = 'undefined'

        return infos

    def get_name(self):

        """ get_name: Returns the name of the network """

        return self._name

    def get_libvirt_name(self):

        """ Returns the name of the Network in libvirt """

        return self._libvirt_name

    def get_ip_host(self):

        """ Return the IP address of the host in the Network """

        return self._ip_host

    def register_host(self, hostname, mac, ip):

        """ Register a host with a static IP address in DHCP """

        logging.debug("registering host {hostname} in network {network}" \
                          .format(hostname=hostname,
                                  network=self._name))
        self._hosts.append({"hostname": hostname, "mac": mac, "ip": ip})

    def created(self):

        """ created: Returns True if Network is created in libvirt """

        return self._virtobj is not None

    def destroy(self):

        """
            Destroys the Network in libvirt
        """

        network = self.find_network()
        if network is None:
            logging.debug("unable to destroy network {name} since not found " \
                          "in libvirt".format(name=self._name))
            return # do nothing and leave
        if network.isActive():
            logging.warn("destroying network {name}".format(name=self._name))
            network.destroy()
        else:
            logging.warn("undefining network {name}".format(name=self._name))
            network.undefine()

    def create(self, overwrite = False):

        """ create: Creates the Network in libvirt """

        if overwrite:
            for network_name in self._conn.listDefinedNetworks():
                if network_name == self._libvirt_name:
                    network = self._conn.networkLookupByName(network_name)
                    logging.info("undefining network " + network_name)
                    network.undefine()
            for network_name in self._conn.listNetworks():
                if network_name == self._libvirt_name:
                    network = self._conn.networkLookupByName(network_name)
                    logging.info("destroying network " + network_name)
                    network.destroy()
            self._virtobj = self._conn.networkCreateXML(self.toxml())
        else:
            if self._libvirt_name in self._conn.listNetworks():
                self._virtobj = self._conn.networkLookupByName(self._libvirt_name)
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

        # Pre-existing bridge, with libvirt >= 0.9.4

        # <network>
        #   <name>host-bridge</name>
        #   <forward mode="bridge"/>
        #   <bridge name="br0"/>
        # </network>

        # root element: network
        element_network = self._doc.createElement("network")
        self._doc.appendChild(element_network)

        # name element
        element_name = self._doc.createElement("name")
        node_name = self._doc.createTextNode(self._libvirt_name)
        element_name.appendChild(node_name)
        element_network.appendChild(element_name)

        # bridge element
        element_bridge = self._doc.createElement("bridge")
        if self._bridge_name is not None:
            element_bridge.setAttribute("name", self._bridge_name)
        element_network.appendChild(element_bridge)

        # forward element
        if self._forward_mode is not None:
            element_forward = self._doc.createElement("forward")
            element_forward.setAttribute("mode", self._forward_mode)
            element_network.appendChild(element_forward)

        # To avoid unwanted behaviour and conflicts on external LAN, DHCP and
        # PXE cannot be enable on bridge forwording networks
        if self._forward_mode is not 'bridge':

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

                # ip/dhcp/host
                for host in self._hosts:
                    element_host = self._doc.createElement("host")
                    element_host.setAttribute("mac", host["mac"])
                    element_host.setAttribute("name", host["hostname"])
                    element_host.setAttribute("ip", host["ip"])
                    element_dhcp.appendChild(element_host)
