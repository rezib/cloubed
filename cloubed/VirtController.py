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
from cloubed.CloubedException import CloubedControllerException

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

    @staticmethod
    def __status_storage_pool(state_code):
        """Returns the name of the status of the StoragePool in Libvirt
           according to its state code

          :param integer xml: the status code
        """

        # Extracted from libvirt API documentation:
        # enum virStoragePoolState {
        #   VIR_STORAGE_POOL_INACTIVE     = 0 Not running
        #   VIR_STORAGE_POOL_BUILDING     = 1 Initializing pool, not available
        #   VIR_STORAGE_POOL_RUNNING      = 2 Running normally
        #   VIR_STORAGE_POOL_DEGRADED     = 3 Running degraded
        #   VIR_STORAGE_POOL_INACCESSIBLE = 4 Running, but not accessible
        #   VIR_STORAGE_POOL_STATE_LAST   = 5
        # }

        states = [ "inactive",
                   "initializing",
                   "active", # voluntarily not 'running' to stay compliant with
                             # 'virsh pool-list' output
                   "degraded",
                   "inaccessible" ]

        if state_code == -1:
            # special value introduced by get_infos() for own Cloubed use when
            # storage pool is not yet defined in Libvirt
            return 'undefined'

        return states[state_code]

    @staticmethod
    def __info_storage_pool(storage_pool):
        """Returns a dict full of key/value string pairs with information about
           the Libvirt storage pool.

           :param libvirt.virStoragePool storage_pool: the storage pool to
               inspect
        """

        infos = {}
        infos['status'] = VirtController.__status_storage_pool(storage_pool.info()[0])
        xml = parseString(storage_pool.XMLDesc(0))
        try:
            element = xml.getElementsByTagName('path').pop()
            infos['path'] = element.childNodes[0].data
        # IndexError exception is passed in order to continue silently
        # if elements are not found in the XML tree
        except IndexError:
            pass
        return infos

    def info_storage_pool(self, path):
        """Returns a dict full of key/value string pairs with information about
           the StoragePool.

           :param string path: the path of the storage pool to look up
           :exceptions CloubedControllerException:
               * a problem is encountered in libvirt
        """

        infos = {}
        storage_pool = self.find_storage_pool(path)
        try:
            if storage_pool is not None:
                infos = VirtController.__info_storage_pool(storage_pool)
            else:
                infos['status'] = VirtController.__status_storage_pool(-1)
        except libvirt.libvirtError as err:
            raise CloubedControllerException(err)
        return infos

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
               * the storage pool in parameter could not be found in libvirt
               * a problem is encountered in libvirt
        """

        # type(pool) is libvirt.virStoragePool
        pool = self.find_storage_pool(storage_pool.path)

        if not pool:
            raise CloubedControllerException("pool {path} not found by "\
                                             "virtualization controller" \
                                             .format(path=storage_pool.path))

        try:
            pool.createXML(xml, 0)
        except libvirt.libvirtError as err:
            raise CloubedControllerException(err)

    @staticmethod
    def __info_storage_volume(storage_volume):
        """Returns a dict with a bunch of infos about a Libvirt storage volume.

           :param libvirt.virStorageVolume storage_volume: the storage volume
               to inspect.
        """
        infos = {}
        infos['status'] = 'active'

        # extract infos out of libvirt XML
        xml = parseString(storage_volume.XMLDesc(0))

        # IndexError exception is passed in order to continue silently
        # if elements are not found in the XML tree

        # path
        try:
            element = xml.getElementsByTagName('path').pop()
            infos['path'] = element.childNodes[0].data
        except IndexError:
            pass

        # capacity/allocation
        try:
            element = xml.getElementsByTagName('capacity').pop()
            capacity = int(element.childNodes[0].data) / 1024**2
            infos['capacity'] = capacity
            element = xml.getElementsByTagName('allocation').pop()
            allocation = int(element.childNodes[0].data) / 1024**2
            infos['allocation'] = allocation
        except IndexError:
            pass
        return infos

    def info_storage_volume(self, storage_pool, name):
        """Returns a dict full of key/value string pairs with information about
           the StorageVolume.

           :param StoragePool storage_pool: a reference to the storage pool in
               which the volume should be found
           :param string name: the name of the filename of the storage volume to
               find
           :exceptions CloubedControllerException:
               * a problem is encountered in libvirt
        """

        infos = {}
        pool_info = self.info_storage_pool(storage_pool.path)
        if pool_info['status'] == 'undefined':
            infos['status'] = "-"
        else:
            storage_volume = self.find_storage_volume(storage_pool, name)
            if storage_volume is not None:
                infos = VirtController.__info_storage_volume(storage_volume)
            else:
                infos['status'] = 'undefined'
        return infos

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

    @staticmethod
    def __info_network(network):
        """Returns a dict with a bunch of infos about a Libvirt network.

           :param libvirt.virNetwork network: the network to inspect
        """

        infos = {}

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

        return infos

    def info_network(self, name):
        """Returns a dict with a bunch of infos about a network in Libvirt.

           :param string name: the name of the network to inspect
           :exceptions CloubedControllerException:
               * a problem is encountered in libvirt
        """

        infos = {}

        try:
            network = self.find_network(name)
            if network is not None:
                infos = VirtController.__info_network(network)
            else:
                infos['status'] = 'undefined'
        except libvirt.libvirtError as err:
            raise CloubedControllerException(err)

        return infos

    def info_networks(self):
        """Returns a dict with a bunch of infos about all networks
           in Libvirt.

           :exceptions CloubedControllerException:
               * a problem is encountered in libvirt
        """

        infos = {}

        try:
            networks = self.conn.listNetworks() + self.conn.listDefinedNetworks()
            for network_name in networks:
                network = self.conn.networkLookupByName(network_name)
                infos[network_name] = VirtController.__info_network(network)
        except libvirt.libvirtError as err:
            raise CloubedControllerException(err)

        return infos

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

    def shutdown_domain(self, domain_name):
        """Shutdown the domain in libvirt whose name is in parameter.

           :param string domain_name: the name of the domain to shutdown
           :exceptions CloubedControllerException:
               * a problem is encountered in libvirt
        """

        domain = self.find_domain(domain_name)
        if domain is not None:
            try:
                domain.shutdown()
            except libvirt.libvirtError as err:
                raise CloubedControllerException(err)

    def reboot_domain(self, domain_name):
        """Gracefully reboot the domain in libvirt whose name is in parameter.

           :param string domain_name: the name of the domain to reboot
           :exceptions CloubedControllerException:
               * a problem is encountered in libvirt
        """

        domain = self.find_domain(domain_name)
        if domain is not None:
            try:
                domain.reboot(0)
            except libvirt.libvirtError as err:
                raise CloubedControllerException(err)

    def reset_domain(self, domain_name):
        """Cold-reset the domain in libvirt whose name is in parameter.

           :param string domain_name: the name of the domain to reset
           :exceptions CloubedControllerException:
               * a problem is encountered in libvirt
        """

        domain = self.find_domain(domain_name)
        if domain is not None:
            try:
                domain.reset(0)
            except libvirt.libvirtError as err:
                raise CloubedControllerException(err)

    def suspend_domain(self, domain_name):
        """Suspend-to-RAM (ACPI S3 state) the domain in libvirt whose name is
           in parameter.

           :param string domain_name: the name of the domain to suspend
           :exceptions CloubedControllerException:
               * a problem is encountered in libvirt
        """

        domain = self.find_domain(domain_name)
        if domain is not None:
            try:
                domain.pMSuspendForDuration( \
                         libvirt.VIR_NODE_SUSPEND_TARGET_MEM, 0, 0)
            except libvirt.libvirtError as err:
                raise CloubedControllerException(err)

    def resume_domain(self, domain_name):
        """Resume a previously suspended domain in libvirt whose name is in
           parameter.

           :param string domain_name: the name of the domain to resume
           :exceptions CloubedControllerException:
               * a problem is encountered in libvirt
        """

        domain = self.find_domain(domain_name)
        if domain is not None:
            try:
                domain.pMWakeup(0)
            except libvirt.libvirtError as err:
                raise CloubedControllerException(err)

    @staticmethod
    def __status_domain(state_code):
        """Returns the name of the status of the Domain in Libvirt
           according to its state code.

          :param integer state_code: the status code
        """

        # Extracted from libvirt API documentation:
        # enum virDomainState {
        #   VIR_DOMAIN_NOSTATE     = 0 no state
        #   VIR_DOMAIN_RUNNING     = 1 the domain is running
        #   VIR_DOMAIN_BLOCKED     = 2 the domain is blocked on resource
        #   VIR_DOMAIN_PAUSED      = 3 the domain is paused by user
        #   VIR_DOMAIN_SHUTDOWN    = 4 the domain is being shut down
        #   VIR_DOMAIN_SHUTOFF     = 5 the domain is shut off
        #   VIR_DOMAIN_CRASHED     = 6 the domain is crashed
        #   VIR_DOMAIN_PMSUSPENDED = 7 the domain is suspended by guest power
        #                              management
        #   VIR_DOMAIN_LAST        = 8 NB: this enum value will increase over
        #                              time as new events are added to the
        #                              libvirt API. It reflects the last state
        #                              supported by this version of the libvirt
        #                              API.
        # }

        states = [ "unknown",
                   "running",
                   "blocked",
                   "paused",
                   "shutdown",
                   "shutoff",
                   "crashed",
                   "suspended" ]

        if state_code == -1:
            # special value introduced by get_infos() for own Cloubed use when
            # domain is not yet defined in Libvirt
            return 'undefined'
        return states[state_code]

    @staticmethod
    def __info_domain(domain):
        """Returns a dict with a bunch of infos about a Libvirt domain.

           :param libvirt.virDomain domain: the domain to inspect
        """
        infos = {}
        # get libvirt status
        infos['status'] = VirtController.__status_domain(domain.info()[0])

        # extract infos out of libvirt XML
        xml = parseString(domain.XMLDesc(0))

        # spice port
        try:
            element = xml.getElementsByTagName('graphics').pop()
            port = element.getAttribute('port')
            type = element.getAttribute('type')
            infos['console'] = type
            infos['port'] = str(port)
        # IndexError exception is passed in order to continue silently
        # if elements are not found in the XML tree
        except IndexError:
            pass
        return infos

    def info_domain(self, name):
        """Returns a dict with a bunch of infos about a domain in Libvirt.

           :param string name: the name of the domain to inspect
           :exceptions CloubedControllerException:
               * a problem is encountered in libvirt
        """
        infos = {}
        domain = self.find_domain(name)
        if domain is not None:
            infos = VirtController.__info_domain(domain)
        else:
            infos['status'] = VirtController.__status_domain(-1)
        return infos

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
