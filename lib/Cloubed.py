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
        # initialize event manager
        #
    
        self._event_manager = EventManager()
        
        #
        # parse configuration file
        #
        configuration_filename = os.path.join(os.getcwd(), "cloubed.yaml")
        self._conf = Configuration(configuration_filename)
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

    def get_domain_by_name(self, name):

        """ get_domain_by_name: """

        for domain in self._domains:
            if domain.get_name() == name:
                return domain

        # domain not found
        raise CloubedException("domain {domain} not found in YAML file " \
                               "{file_name}" \
                                   .format(domain=name,
                                           file_name=self._conf.get_file_path()))

    def get_templates_dict(self):

        """ get_templates_dict: """

        return self._conf.get_templates_dict()

    def serve_http(self, address):
        
        """ server_http: """

        if self._http_server is not None:
            if not self._http_server.launched():
                logging.debug("launching HTTP server on address {address}" \
                                  .format(address=address))
                self._http_server.launch(address)

    def gen_file(self, domain_name, template_name):

        """ gen_file: """

        templates_dict = self.get_templates_dict()

        domain = self.get_domain_by_name(domain_name)
        domain_template = domain.get_template_by_name(template_name)
        domain_template.render(templates_dict)

    def boot_vm(self, domain_name, bootdev = "hd", overwrite_disks = [], recreate_networks = []):

        """ boot_vm: """

        domain = self.get_domain_by_name(domain_name)
        try:
            if type(overwrite_disks) == bool:
                if overwrite_disks == True:
                    overwrite_disks = [ disk.get_storage_volume().get_name() \
                                            for disk in domain.get_disks() ]
                else:
                    overwrite_disks = []
            if type(recreate_networks) == bool:
                if recreate_networks == True:
                    recreate_networks = [ netif.get_network().get_name() \
                                              for netif in domain.get_netifs() ]
                else:
                    recreate_networks = []

            domain.create(bootdev, overwrite_disks, recreate_networks, True)

        except libvirt.libvirtError as err:
            logging.error("libvirt error: {error}".format(error=err))
            raise CloubedException(err)

    def wait_event(self, domain_name, event_type, event_detail, enable_http = True):

        """ wait_event: """

        # search the domain
        domain = self.get_domain_by_name(domain_name)

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

    def clean_exit(self):

        logging.debug("clean exit")
        if self._http_server.launched():
            self._http_server.terminate()
        self._event_manager.terminate()
