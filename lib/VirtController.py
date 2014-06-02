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

# still to implement:
#  _virtobj[virStoragePool].create()
#  _virtobj[virStoragePool].isActive()

import libvirt
import logging
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

    def listStoragePools(self):
        """Returns list
        """
        try:
            return self.conn.listStoragePools()
        except libvirt.libvirtError as err:
            raise CloubedControllerException(err)

    def listDefinedStoragePools(self):
        """Returns list
        """

        try:
            return self.conn.listDefinedStoragePools()
        except libvirt.libvirtError as err:
            raise CloubedControllerException(err)

    def storagePoolLookupByName(self, name):
        """Returns libvirt.virStoragePool
        """

        try:
            return self.conn.storagePoolLookupByName(name)
        except libvirt.libvirtError as err:
            raise CloubedControllerException(err)

    def storagePoolCreateXML(self, xml, flags):
        """Returns libvirt.virStoragePool
        """

        try:
            return self.conn.storagePoolCreateXML(xml, flags)
        except libvirt.libvirtError as err:
            raise CloubedControllerException(err)

    #
    # networks
    #

    def listNetworks(self):
        """Returns list
        """

        try:
            return self.conn.listNetworks()
        except libvirt.libvirtError as err:
            raise CloubedControllerException(err)

    def listDefinedNetworks(self):
        """Returns list
        """

        try:
            return self.conn.listDefinedNetworks()
        except libvirt.libvirtError as err:
            raise CloubedControllerException(err)

    def networkLookupByName(self, name):
        """Returns libvirt.virNetwork
        """

        try:
            return self.conn.networkLookupByName(name)
        except libvirt.libvirtError as err:
            raise CloubedControllerException(err)

    def networkCreateXML(self, xml):
        """Returns libvirt.virNetwork
        """

        try:
            return self.conn.networkCreateXML(xml)
        except libvirt.libvirtError as err:
            raise CloubedControllerException(err)

    #
    # domains
    #

    def listDefinedDomains(self):
        """Returns list
        """

        try:
            return self.conn.listDefinedDomains()
        except libvirt.libvirtError as err:
            raise CloubedControllerException(err)

    def listDomainsID(self):
        """Returns list
        """

        try:
            return self.conn.listDomainsID()
        except libvirt.libvirtError as err:
            raise CloubedControllerException(err)

    def lookupByName(self, name):
        """Returns libvirt.virDomain
        """

        try:
            return self.conn.lookupByName(name)
        except libvirt.libvirtError as err:
            raise CloubedControllerException(err)

    def lookupByID(self, id):
        """Returns libvirt.virDomain
        """

        try:
            return self.conn.lookupByID(id)
        except libvirt.libvirtError as err:
            raise CloubedControllerException(err)

    def createXML(self, xml, flags):
        """Returns libvirt.virDomain
        """

        try:
            return self.conn.createXML(xml, flags)
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

class VirtController2(libvirt.virConnect):
    """This class could be used to log all libvirt calls made by other classes of
       Cloubed. It is not really intended to be used for other purpose.
    """


    def __new__(cls, read_only=False):

        if not read_only:
            logging.debug("new RW VirtController2")
            conn = libvirt.open("qemu:///system")
        else:
            logging.debug("new RO VirtController2")
            conn = libvirt.openReadOnly("qemu:///system")

        # override the type from virConnect to VirtController
        conn.__class__ = cls

        return conn

    def __init__(self, **kwargs):
    
        # avoid calling virConnect.__init__() here since it has already been
        # called before in __new__() within method open()/openReadOnly()
        pass

    def __getattribute__(self, name):

        attr = object.__getattribute__(self, name)
        if hasattr(attr, '__call__'):
            def newfunc(*args, **kwargs):
                logging.debug('call virConnect.{call}()'.format(call=attr.__name__))
                result = attr(*args, **kwargs)
                logging.debug('call virConnect.{call}(): answer type {type}' \
                                  .format(call=attr.__name__,
                                          type=type(result)))
                return result
            return newfunc
        else:
            return attr

    #
    # Event Management
    #

    @staticmethod
    def event_register():
        libvirt.virEventRegisterDefaultImpl()

    @staticmethod
    def event_run():
        if libvirt is not None: libvirt.virEventRunDefaultImpl()

    def domain_event_register(self, handler):
        self.domainEventRegisterAny(None,
                                    libvirt.VIR_DOMAIN_EVENT_ID_LIFECYCLE,
                                    handler,
                                    None)

# TODO:
#   write VirtController class with self.conn attribute
#   write all needed methods for Domain, Network, Storage* classes
#   write EventManager related stuff


