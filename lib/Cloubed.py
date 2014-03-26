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

""" Cloubed """

import libvirt
import sys
import os
import logging
import thread

from StoragePool import StoragePool
from StorageVolume import StorageVolume
from Domain import Domain
from Network import Network
from EventManager import EventManager
from conf.Configuration import Configuration
from conf.ConfigurationLoader import ConfigurationLoader
from HTTPServer import HTTPServer
from DomainEvent import DomainEvent
from CloubedException import CloubedException

class Singleton(type):

    """ Singleton metaclass """

    __instances = {}
    __lockObj = thread.allocate_lock()  # lock object

    def __call__(mcs, *args, **kwargs):
        mcs.__lockObj.acquire()
        try:
            if mcs not in mcs.__instances:
                mcs.__instances[mcs] = super(Singleton, mcs) \
                                           .__call__(*args, **kwargs)
        finally:
            #  Exit from critical section whatever happens
            mcs.__lockObj.release()

        return mcs.__instances[mcs]

    def initialized(mcs):

         return mcs in mcs.__instances

class Cloubed():

    """ Cloubed main class """

    __metaclass__ = Singleton

    def __init__(self):

        #
        # connection to the hypervisor
        #
        
        self._conn = libvirt.open("qemu:///system")
        if self._conn == None:
            logging.error("Failed to open connection to the hypervisor")
            sys.exit(1)

        #
        # EventManager, None at the beginning. Initialized by
        # self.launch_event_manager() in self.wait_event()
        #
        self._event_manager = None
        
        #
        # parse configuration file
        #
        configuration_filename = os.path.join(os.getcwd(), "cloubed.yaml")
        self._conf_loader = ConfigurationLoader(configuration_filename)
        self._conf = Configuration(self._conf_loader)
        self._name = self._conf.get_testbed_name()
    
        #
        # initialize storage pools
        #    
        self._storage_pools = []
        for storage_pool_conf in self._conf.get_storage_pools_list():
            logging.info("initializing storage pool {name}" \
                             .format(name=storage_pool_conf.get_name()))
            self._storage_pools.append(StoragePool(self._conn,
                                                   storage_pool_conf))
    
        #
        # initialize storage volumes
        #
        self._storage_volumes = []
        for storage_volume_conf in self._conf.get_storage_volumes_list():
            logging.info("initializing storage volume {name}" \
                             .format(name=storage_volume_conf.get_name()))
            self._storage_volumes.append(StorageVolume(self._conn,
                                                       storage_volume_conf))
    
        #
        # initialize networks
        #
        self._networks = []
        for network_conf in self._conf.get_networks_list():
            logging.info("initializing network {name}" \
                             .format(name=network_conf.get_name()))
            self._networks.append(Network(self._conn,
                                          network_conf))

        #
        # initialize domain and templates
        #
        self._domains = []
        for domain_conf in self._conf.get_domains_list():
            logging.info("initializing domain {name}" \
                             .format(name=domain_conf.get_name()))
            self._domains.append(Domain(self._conn,
                                        domain_conf))

        #
        # initialize http server, arbitrary select first host ip
        # found in cloubed yaml file
        #
        self._http_server = HTTPServer()

    def storage_pools(self):

        """ Returns the list of storage pools names """

        return [ storage_pool.get_name() \
                 for storage_pool in self._storage_pools ]

    def storage_volumes(self):

        """ Returns the list of storage volumes names """

        return [ storage_volume.get_name() \
                 for storage_volume in self._storage_volumes ]

    def networks(self):

        """ Returns the list of networks names """

        return [ network.get_name() for network in self._networks ]

    def domains(self):

        """ Returns the list of domains names """

        return [ domain.get_name() for domain in self._domains ]

    def get_domain_by_name(self, name):

        """ get_domain_by_name: """

        for domain in self._domains:
            if domain.get_name() == name:
                return domain

        # domain not found
        raise CloubedException("domain {domain} not found in configuration"
                                   .format(domain=name))

    def get_network_by_name(self, name):

        """
            Returns the Network object whose name is given in parameter. Raises
            exception if not found.
        """

        for network in self._networks:
            if network.get_name() == name:
                return network

        # network not found
        raise CloubedException("network {network} not found in configuration"
                                   .format(network=name))

    def get_storage_volume_by_name(self, name):

        """
            Returns the StorageVolume object whose name is given in parameter.
            Raises exception if not found.
        """

        for storage_volume in self._storage_volumes:
            if storage_volume.get_name() == name:
                return storage_volume

        # storage volume not found
        raise CloubedException("storage volume {storage_volume} not found in " \
                               "configuration".format(storage_volume=name))

    def get_storage_pool_by_name(self, name):

        """
            Returns the StoragePool object whose name is given in parameter.
            Raises exception if not found.
        """

        for storage_pool in self._storage_pools:
            if storage_pool.get_name() == name:
                return storage_pool

        # storage pool not found
        raise CloubedException("storage pool {storage_pool} not found in " \
                               "configuration".format(storage_pool=name))

    def get_templates_dict(self, domain_name):

        """ get_templates_dict: """

        templates_dict = self._conf.get_templates_dict(domain_name)
        return templates_dict

    def serve_http(self, address):
        
        """ server_http: """

        if self._http_server is not None:
            if not self._http_server.launched():
                logging.debug("launching HTTP server on address {address}" \
                                  .format(address=address))
                self._http_server.launch(address)

    def launch_event_manager(self):

        """ Launch event manager thread unless already done """

        if self._event_manager is None:
            self._event_manager = EventManager()

    def gen_file(self, domain_name, template_name):

        """ gen_file: """

        templates_dict = self.get_templates_dict(domain_name)

        domain = self.get_domain_by_name(domain_name)
        domain_template = domain.get_template_by_name(template_name)
        domain_template.render(templates_dict)

    def boot_vm(self, domain_name, bootdev = "hd", overwrite_disks = [], recreate_networks = []):

        """ boot_vm: """

        domain = self.get_domain_by_name(domain_name)
        try:
            if type(overwrite_disks) == bool:
                if overwrite_disks == True:
                    overwrite_disks = domain.get_disks()
                else:
                    overwrite_disks = []
            else:
                # type(overwrite_disks) is list
                # remove non-existing disks and log warning
                domain_disks = domain.get_disks()
                for disk in set(overwrite_disks) - set(domain_disks):
                    logging.warning("domain {domain} does not have disk " \
                                    "{disk}, removing it of disks to " \
                                    "overwrite" \
                                        .format(domain=domain.get_name(),
                                                disk=disk))
                    overwrite_disks.remove(disk)

            logging.debug("disks to overwrite for domain {domain}: {disks}" \
                              .format(domain=domain.get_name(),
                                      disks=str(overwrite_disks)))

            if type(recreate_networks) == bool:
                if recreate_networks == True:
                    recreate_networks = domain.get_networks()
                else:
                    recreate_networks = []
            else:
                # type(recreate_networks) is list
                # remove non-existing networks and log warning
                domain_networks = domain.get_networks()
                for network in set(recreate_networks) - set(domain_networks):
                    logging.warning("domain {domain} is not connected to " \
                                    "network {network}, removing it of " \
                                    "networks to recreate" \
                                        .format(domain=domain.get_name(),
                                                network=network))
                    recreate_networks.remove(network)

            logging.debug("networks to recreate for domain {domain}: " \
                          "{networks}" \
                              .format(domain=domain.get_name(),
                                      networks=str(recreate_networks)))

            domain.create(bootdev, overwrite_disks, recreate_networks, True)

        except libvirt.libvirtError as err:
            logging.error("libvirt error: {error}".format(error=err))
            raise CloubedException(err)

    def create_network(self, network_name, recreate):

        """ Create network in Cloubed """
        network = self.get_network_by_name(network_name)
        try:
            network.create(recreate)
        except libvirt.libvirtError as err:
            raise CloubedException(err)

    def wait_event(self, domain_name, event_type, event_detail, enable_http = True):

        """ wait_event: """

        # search the domain
        domain = self.get_domain_by_name(domain_name)

        # launch event manager tread
        self.launch_event_manager()

        if enable_http:
            # build the list of host ip addresses on all networks connected to
            # the domain
            list_ip_hosts = [ dom_netif.get_network().get_ip_host() \
                              for dom_netif in domain.get_netifs() \
                              if dom_netif.get_network().get_ip_host() \
                                 is not None ]
            if len(list_ip_hosts) > 0:
                # arbitrary take the first ip address
                address = list_ip_hosts[0]
                self.serve_http(address)
            else:
                logging.debug("HTTP server not launched because no host IP " \
                              "address on networks connected to domain " \
                              "{domain}".format(domain=domain_name))

        domain_event = DomainEvent("{event_type}" \
                                   .format(event_type=event_type.upper()),
                                   "{event_type}_{event_detail}" \
                                   .format(event_type=event_type.upper(),
                                           event_detail=event_detail.upper()))
        domain.wait_for_event(domain_event)

    def get_infos(self):
        """
            Returns a dict full of information about the testbed and its
            resources
        """

        infos = {}

        infos['storagepools'] = {}
        for storage_pool in self._storage_pools:
            name = storage_pool.get_name()
            infos['storagepools'][name] = storage_pool.get_infos()

        infos['storagevolumes'] = {}
        for storage_volume in self._storage_volumes:
            name = storage_volume.get_name()
            infos['storagevolumes'][name] = storage_volume.get_infos()

        infos['networks'] = {}
        for network in self._networks:
            name = network.get_name()
            infos['networks'][name] = network.get_infos()

        infos['domains'] = {}
        for domain in self._domains:
            name = domain.get_name()
            infos['domains'][name] = domain.get_infos()

        return infos

    def cleanup(self):

        for domain in self._domains:
            domain.destroy()
        for network in self._networks:
            network.destroy()
        for storage_volume in self._storage_volumes:
            storage_volume.destroy()
        for storage_pool in self._storage_pools:
            storage_pool.destroy()

    def xml(self, resource_type, resource_name):

        if resource_type == "domain":
            domain = self.get_domain_by_name(resource_name)
            return domain.xml()
        elif resource_type == "network":
            network = self.get_network_by_name(resource_name)
            return network.xml()
        elif resource_type == "storagevolume":
            storage_volume = self.get_storage_volume_by_name(resource_name)
            return storage_volume.xml()
        elif resource_type == "storagepool":
            network = self.get_storage_pool_by_name(resource_name)
            return network.xml()
        else:
            raise CloubedException("cannot dump XML of invalid resource type " \
                                   "{type}".format(type=resource_type))

    def clean_exit(self):

        logging.debug("clean exit")
        if self._http_server.launched():
            self._http_server.terminate()
        if self._event_manager is not None:
            self._event_manager.terminate()
