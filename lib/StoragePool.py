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

""" StoragePool class of Cloubed """

import logging
from xml.dom.minidom import Document

class StoragePool:

    """ StoragePool class """

    _storage_pools = []

    def __init__(self, conn, storage_pool_conf):

        self._conn = conn
        self._virtobj = None

        self._name = storage_pool_conf.get_name()
        self._path = storage_pool_conf.get_path()

        StoragePool._storage_pools.append(self)

        self._doc = None
        self.__init_xml()

    def __del__(self):

        StoragePool._storage_pools.remove(self)

    def __eq__(self, other): # needed for __del__

        return self._name == other.get_name()

    @classmethod
    def get_storage_pools_list(cls):

        """
            get_storage_pools_list: Returns the list of existing StoragePools
        """

        return cls._storage_pools

    @classmethod
    def get_storage_pool_by_name(cls, storage_pool_name):

        """
            get_storage_pool_by_name: Returns the StoragePool with the name
                                      given in parameter
        """

        for storage_pool in cls._storage_pools:
            if storage_pool.get_name() == storage_pool_name:
                return storage_pool

        return None

    def toxml(self):

        """
            toxml: Returns the libvirt XML representation of the StoragePool
        """

        return self._doc.toxml()

    def getvirtobj(self):

        """
            getvirtobj: Returns the libvirt object of the StoragePool
        """

        return self._virtobj

    def getpath(self):

        """
            getpath: Returns the path of the StoragePool
        """

        return self._path

    def get_name(self):

        """
            get_name: Returns the name of the StoragePool
        """

        return self._name

    def created(self):

        """
            created: Returns True if the StoragePool is created in libvirt
        """

        return self._virtobj is not None

    def create(self, overwrite = False):

        """
            create: Creates the StoragePool in libvirt
        """

        if overwrite:
            # Delete all existing storage pools.
            # BUG: Does not do anything more clever since not found in libvirt
            # how to get path of an existing or defined storage pool and check
            # for potential conflict.
            for sp_name in self._conn.listDefinedStoragePools():
                storage_pool = self._conn.storagePoolLookupByName(sp_name)
                logging.info("undefining storage pool " + sp_name)
                storage_pool.undefine()
            for sp_name in self._conn.listStoragePools():
                storage_pool = self._conn.storagePoolLookupByName(sp_name)
                logging.info("destroying storage pool " + sp_name)
                storage_pool.destroy()
            self._virtobj = self._conn.storagePoolCreateXML(self._doc.toxml(), 0)
        else:
            if self._name in self._conn.listStoragePools():
                self._virtobj = self._conn.storagePoolLookupByName(self._name)
            else:
                self._virtobj = self._conn.storagePoolCreateXML(self._doc.toxml(), 0)

    def __init_xml(self):

        """
            __init_xml: Generate the libvirt XML representation of the
                        StoragePool
        """

        self._doc = Document()

        # <pool type="dir">
        #   <name>poolname</name>
        #   <target>
        #     <path>/absolute/path</path>
        #   </target>
        # </pool>

        # root node: pool
        element_pool = self._doc.createElement("pool")
        element_pool.setAttribute("type","dir")
        self._doc.appendChild(element_pool)

        # name node
        element_name = self._doc.createElement("name")
        node_name = self._doc.createTextNode(self._name)
        element_name.appendChild(node_name)
        element_pool.appendChild(element_name)

        # target node
        element_target = self._doc.createElement("target")
        element_pool.appendChild(element_target)

        # path node
        element_path = self._doc.createElement("path")
        node_path = self._doc.createTextNode(self._path)
        element_path.appendChild(node_path)
        element_target.appendChild(element_path)
