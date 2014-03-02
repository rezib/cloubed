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
from xml.dom.minidom import Document, parseString
from Utils import getuser

class StoragePool:

    """ StoragePool class """

    _storage_pools = []

    def __init__(self, conn, storage_pool_conf):

        self._conn = conn
        self._virtobj = None

        self._name = storage_pool_conf.get_name()
        use_namespace = True # should better be a conf parameter in the future
        if use_namespace:    # logic should moved be in an abstract parent class
            self._libvirt_name = \
                "{user}:{testbed}:{name}" \
                    .format(user = getuser(),
                            testbed = storage_pool_conf.get_testbed(),
                            name = self._name)
        else:
            self._libvirt_name = self._name
        self._path = storage_pool_conf.get_path()

        StoragePool._storage_pools.append(self)

        self._doc = None

    def __del__(self):

        try:
            StoragePool._storage_pools.remove(self)
        except ValueError:
            pass

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

    def xml(self):

        """
            Returns the libvirt XML representation of the StoragePool
        """

        self.__init_xml()
        return self._doc

    def toxml(self):

        """
            Returns the libvirt XML representation of the StoragePool as string
        """

        return self.xml().toxml()

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

    def find_storage_pool(self):

        """
            Search for any storage pool with the same path among all defined
            and active storage pools in Libvirt. If one matches, returns it.
            Returns None if not found.
        """

        all_pools = self._conn.listStoragePools() + self._conn.listDefinedStoragePools()
        for storage_pool_name in all_pools:

            storage_pool = self._conn.storagePoolLookupByName(storage_pool_name)

            xml = storage_pool.XMLDesc(0)
            path = StoragePool.extract_path(xml)

            if path == self._path:

                logging.info("found storage pool {name} with the same path" \
                                 .format(name=storage_pool_name))
                return storage_pool

        return None

    def get_infos(self):
        """
            Returns a dict full of key/value string pairs with information about
            the StoragePool
        """

        infos = {}

        storage_pool = self.find_storage_pool()

        if storage_pool is not None:

            infos['status'] = StoragePool.__get_status(storage_pool.info()[0])

            # extract infos out of libvirt XML
            xml = parseString(storage_pool.XMLDesc(0))

            # IndexError exception is passed in order to continue silently
            # if elements are not found in the XML tree

            # path
            try:
                element = xml.getElementsByTagName('path').pop()
                infos['path'] = element.childNodes[0].data
            except IndexError:
                pass

        else:

            infos['status'] = StoragePool.__get_status(-1)

        return infos

    def get_status(self):
        """
            Returns the status name of the StoragePool from Libvirt standpoint
            extracted out of the dict returned by get_infos(). This method is
            called internally by StorageVolume class.
        """

        return self.get_infos()['status']

    @staticmethod
    def __get_status(state_code):
        """
            Returns the name of the status of the StoragePool in Libvirt
            according to its state code
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

    def get_libvirt_name(self):

        """
            Returns the name of the StoragePool in libvirt
        """

    def destroy(self):

        """
            Destroys the StoragePool in libvirt.
        """

        storage_pool = self.find_storage_pool()
        if storage_pool is None:
            logging.debug("unable to destroy storage pool {name} since not " \
                          "found in libvirt".format(name=self._name))
            return # do nothing and leave

        if storage_pool.isActive():
            # The storage pool can only by destroyed if it has not any volume,
            # including volume of other testbeds
            nb_vols = storage_pool.numOfVolumes()
            if nb_vols == 0:
                logging.warn("destroying storage pool {name}".format(name=self._name))
                storage_pool.destroy()
            else:
                logging.warn("unable storage pool {name} because it still has " \
                             "{nb} volumes".format(name=self._name, nb=nb_vols))
        else:
            logging.warn("undefining storage pool {name}".format(name=self._name))
            storage_pool.undefine()

    def create(self):

        """
            Creates the StoragePool in libvirt. If it already exists, simply
            link to it.
        """

        storage_pool = self.find_storage_pool()

        if storage_pool is not None:
            logging.info("found storage pool {name} with the same path" \
                             .format(name=storage_pool.name()))
            self._virtobj = storage_pool
            self._libvirt_name = storage_pool.name() # override libvirt name

            # if not active in libvirt (defined but not started), activate it
            if not self._virtobj.isActive():
                logging.info("storage pool {name} is not active, activating it..." \
                                 .format(name=self._libvirt_name))
                self._virtobj.create(0)

        else:
            self._virtobj = self._conn.storagePoolCreateXML(self.toxml(), 0)

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
        node_name = self._doc.createTextNode(self._libvirt_name)
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

    @staticmethod
    def extract_path(xml_str):

        xml = parseString(xml_str)
        return xml.getElementsByTagName(u'path')[0].firstChild.data
