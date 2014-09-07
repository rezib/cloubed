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
from Utils import getuser, net_conflict
from CloubedException import CloubedException

class Network:

    """ Network class """

    def __init__(self, tbd, network_conf):

        self.tbd = tbd
        self.ctl = self.tbd.ctl

        self.name = network_conf.name
        use_namespace = True # should better be a conf parameter in the future
        if use_namespace:    # logic should moved be in an abstract parent class
            self.libvirt_name = \
                "{user}:{testbed}:{name}" \
                    .format(user = getuser(),
                            testbed = network_conf.testbed,
                            name = self.name)
        else:
            self.libvirt_name = self.name

        self._forward_mode = network_conf.forward_mode
        self._bridge_name = network_conf.bridge_name

        self._with_local_settings = False
        self.ip_host = None
        self._netmask = None
        if network_conf.has_local_settings():
            self._with_local_settings = True
            self.ip_host = network_conf.ip_host
            self._netmask = network_conf.netmask

        self._with_dhcp = False
        self._dhcp_range_start = None
        self._dhcp_range_stop = None
        if network_conf.has_dhcp():
            self._with_dhcp = True
            self._dhcp_range_start = network_conf.dhcp_start
            self._dhcp_range_end = network_conf.dhcp_end

        self._domain = network_conf.domain

        self._with_pxe = False
        self._tftproot = None
        self._bootfile = None
        if network_conf.has_pxe():
            self._with_pxe = True
            self._tftproot = network_conf.pxe_tftp_dir
            self._bootfile = network_conf.pxe_boot_file

        # list of statically declared hosts in the network
        self._hosts = []

        self._doc = None

    def xml(self):

        """ Returns the libvirt XML representation of the Network """

        self.__init_xml()
        return self._doc

    def toxml(self):

        """ Returns the libvirt XML representation of the Network as string """

        return self.xml().toxml()

    def get_infos(self):
        """Returns a dict full of key/value string pairs with information about
           the Network.
        """
        return self.ctl.info_network(self.libvirt_name)

    def register_host(self, hostname, mac, ip):

        """ Register a host with a static IP address in DHCP """

        logging.debug("registering host {hostname} in network {network}" \
                          .format(hostname=hostname,
                                  network=self.name))
        self._hosts.append({"hostname": hostname, "mac": mac, "ip": ip})

    def destroy(self):

        """
            Destroys the Network in libvirt
        """

        network = self.ctl.find_network(self.libvirt_name)
        if network is None:
            logging.debug("unable to destroy network {name} since not found " \
                          "in libvirt".format(name=self.name))
            return # do nothing and leave
        if network.isActive():
            logging.warn("destroying network {name}".format(name=self.name))
            network.destroy()
        else:
            logging.warn("undefining network {name}".format(name=self.name))
            network.undefine()

    def __check_conflict(self):
        """It looks over existing active networks in Libvirt in order to detect
           potential conflicting IP settings. If yes, it returns a tuple with
           True and the name of the first conflicting network. Else it returns
           a tuple with False and None.
        """
        infos = self.ctl.info_networks()
        for network_name, network_infos in infos.iteritems():
            if network_name != self.libvirt_name and \
                network_infos['status'] == 'active':
                if net_conflict(self.ip_host, self._netmask,
                               network_infos.get('ip'),
                               network_infos.get('netmask')):
                    return (True, network_name)
        return (False, None)

    def create(self, overwrite=False):
        """Creates the Network in libvirt. First, it searches if the network
           has already been created previously, based on its name. If yes and
           overwrite parameter is True, it will delete the previous Network and
           creates this one instead. If yes and overwrite is False, it does not
           do anything. Else, it creates the networks.
           Before creating the network, it checks if another active Network has
           conflicting IP settings. If yes, a CloubedException is raised.

           :exceptions CloubedException:
               * another active network with conflicting IP settings has been
                 found in Libvirt.
        """

        network = self.ctl.find_network(self.libvirt_name)
        found = network is not None
        create = False

        if found and overwrite:
            if network.isActive():
                logging.info("destroying network {name}".format(name=self.name))
                network.destroy()
            else:
                logging.info("undefining network {name}".format(name=self.name))
                network.undefine()
            create = True
        elif not found:
            create = True

        if create:
            conflict, network_name = self.__check_conflict()
            if conflict:
                raise CloubedException("another network {network} is already " \
                                       "active with conflicting IP settings" \
                                           .format(network=network_name))
            else:
                self.ctl.create_network(self.toxml())

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
        #   <domain name="example.net">
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
        node_name = self._doc.createTextNode(self.libvirt_name)
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

        # domain
        if self._domain:
            element_domain = self._doc.createElement("domain")
            element_domain.setAttribute("name", self._domain)
            element_network.appendChild(element_domain)

        # To avoid unwanted behaviour and conflicts on external LAN, DHCP and
        # PXE cannot be enable on bridge forwording networks
        if self._forward_mode is not 'bridge':

            # ip element
            if self._with_local_settings:
                element_ip = self._doc.createElement("ip")
                element_ip.setAttribute("address", self.ip_host)
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
