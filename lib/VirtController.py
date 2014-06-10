#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2014 Rémi Palancher 
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

""" Cloubed VirtController class
    All calls to libvirt library are made through this file.
"""

import libvirt
import logging
from xml.dom.minidom import parseString
from CloubedException import CloubedControllerException

class VirtController(object):

    def __init__(self, read_only=False):

        if not read_only:
            logging.debug("new RW VirtController")
            self.conn = libvirt.open("qemu:///system")
        else:
            logging.debug("new RO VirtController")
            self.conn = libvirt.openReadOnly("qemu:///system")

    #
    # storage pools
    #

    def find_storage_pool(self, path):
        """Search for any storage pool with the same path among all defined
           and active storage pools in Libvirt. If one matches, returns it or
           None if not found.

           :param string path: the absolute path of the storage pool to find
           :exceptions CloubedControllerException:
               * a problem is encountered in libvirt
        """

        try:
            all_pools = self.conn.listStoragePools() + self.conn.listDefinedStoragePools()
            for storage_pool_name in all_pools:

                storage_pool = self.conn.storagePoolLookupByName(storage_pool_name)

                xml = storage_pool.XMLDesc(0)
                dom = parseString(xml)
                cur_path = dom.getElementsByTagName(u'path')[0].firstChild.data

                if cur_path == path:

                    logging.info("found storage pool {name} with the same path" \
                                     .format(name=storage_pool_name))
                    return storage_pool

            return None

        except libvirt.libvirtError as err:
            raise CloubedControllerException(err)

    def create_storage_pool(self, xml):
        """Create a new storage pool in libvirt based on the XML description in
           the string parameter.

           :param string xml: the XML description of the storage pool to create
           :exceptions CloubedControllerException:
               * a problem is encountered in libvirt
        """

        try:
            self.conn.storagePoolCreateXML(xml, 0)
        except libvirt.libvirtError as err:
            raise CloubedControllerException(err)

    #
    # storage volumes
    #

    def find_storage_volume(self, storage_pool, name):
        """Search for any storage volume with the same name among all defined
           storage volumes within the storage pool in Libvirt. If one matches,
           returns it as libvirt.virStorageVol or None if not found.

           :param StoragePool storage_pool: a reference to the storage pool in
               which the volume should be found
           :param string name: the name of the filename of the storage volume to
               find
           :exceptions CloubedControllerException:
               * a problem is encountered in libvirt
        """

        # type(pool) is libvirt.virStoragePool
        pool = self.find_storage_pool(storage_pool.path)

        try:
            if pool is not None:
                for storage_volume_name in pool.listVolumes():
                    if storage_volume_name == name:
                        return pool.storageVolLookupByName(storage_volume_name)
        except libvirt.libvirtError as err:
            raise CloubedControllerException(err)

        return None

    def create_storage_volume(self, storage_pool, xml):
        """Create a new storage volume in libvirt based on the XML description
           in parameter.

           :param StoragePool storage_pool: a reference to the storage pool in
               which the volume will be created
           :param string xml: the XML description of the storage volume to create
           :exceptions CloubedControllerException:
               * a problem is encountered in libvirt
        """

        # type(pool) is libvirt.virStoragePool
        pool = self.find_storage_pool(storage_pool.path)

        try:
            pool.createXML(xml, 0)
        except libvirt.libvirtError as err:
            raise CloubedControllerException(err)

    #
    # networks
    #

    def find_network(self, name):
        """Search for network with the same name among all defined and active
           networks in Libvirt. If one matches, returns it as libvirt.virNetwork
           or None if not found.

           :param string name: the name of the network to find
           :exceptions CloubedControllerException:
               * a problem is encountered in libvirt
        """

        try:
            networks = self.conn.listNetworks() + self.conn.listDefinedNetworks()
            for network_name in networks:
                if network_name == name:
                    return self.conn.networkLookupByName(network_name)
        except libvirt.libvirtError as err:
            raise CloubedControllerException(err)

        return None

    def create_network(self, xml):
        """Create a new network in libvirt based on the XML description in
           parameter.

           :param string xml: the XML description of the network to create
           :exceptions CloubedControllerException:
               * a problem is encountered in libvirt
        """

        try:
            self.conn.networkCreateXML(xml)
        except libvirt.libvirtError as err:
            raise CloubedControllerException(err)

    #
    # domains
    #

    def find_domain(self, name):
        """Search for domain with the same name among all defined and active
           domains in Libvirt. If one matches, returns it as libvirt.virDomain
           or None if not found.

           :param string name: the name of the domain to find
           :exceptions CloubedControllerException:
               * a problem is encountered in libvirt
        """

        try:
            # workaround since no way to directly get list of names of all
            # active domains in Libvirt API
            active_domains = [ self.conn.lookupByID(domain_id).name() \
                                   for domain_id in self.conn.listDomainsID() ]

            domains = active_domains + self.conn.listDefinedDomains()
            for domain_name in domains:
                if domain_name == name:
                    return self.conn.lookupByName(domain_name)
        except libvirt.libvirtError as err:
            raise CloubedControllerException(err)

        return None

    def create_domain(self, xml):
        """Create a new domain in libvirt based on the XML description in
           parameter.

           :param string xml: the XML description of the domain to create
           :exceptions CloubedControllerException:
               * a problem is encountered in libvirt
        """

        try:
            self.conn.createXML(xml, 0)
        except libvirt.libvirtError as err:
            raise CloubedControllerException(err)

    #
    # event management
    #

    @staticmethod
    def event_register():

        libvirt.virEventRegisterDefaultImpl()

    @staticmethod
    def event_run():

        if libvirt is not None: libvirt.virEventRunDefaultImpl()

    def setKeepAlive(self, major, minor):
        """Returns void
        """

        self.conn.setKeepAlive(major, minor)

    def domain_event_register(self, handler):
        """Returns void
        """

        self.conn.domainEventRegisterAny(None,
                                         libvirt.VIR_DOMAIN_EVENT_ID_LIFECYCLE,
                                         handler,
                                         None)
    #
    # Support testing methods
    #

    @staticmethod
    def supports_spice():
        return libvirt.getVersion() >= 8006
