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

    def __init__(self, tbd, storage_pool_conf):

        self.tbd = tbd
        self.ctl = self.tbd.ctl

        self.name = storage_pool_conf.name
        use_namespace = True # should better be a conf parameter in the future
        if use_namespace:    # logic should moved be in an abstract parent class
            self.libvirt_name = \
                "{user}:{testbed}:{name}" \
                    .format(user = getuser(),
                            testbed = storage_pool_conf.testbed,
                            name = self.name)
        else:
            self.libvirt_name = self.name
        self.path = storage_pool_conf.path

        self._doc = None

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

    def get_infos(self):
        """Returns a dict full of key/value string pairs with information about
           the StoragePool.
        """
        return self.ctl.info_storage_pool(self.path)

    def get_status(self):
        """Returns the status name of the StoragePool from VirtController
           standpoint extracted out of the dict returned by get_infos().
           This method is called by StorageVolume class.
        """
        return self.get_infos()['status']

    def destroy(self):

        """
            Destroys the StoragePool in libvirt.
        """

        storage_pool = self.ctl.find_storage_pool(self.path)
        if storage_pool is None:
            logging.debug("unable to destroy storage pool {name} since not " \
                          "found in libvirt".format(name=self.name))
            return # do nothing and leave

        if storage_pool.isActive():
            # The storage pool can only by destroyed if it has not any volume,
            # including volume of other testbeds
            nb_vols = storage_pool.numOfVolumes()
            if nb_vols == 0:
                logging.warn("destroying storage pool {name}".format(name=self.name))
                storage_pool.destroy()
            else:
                logging.warn("unable storage pool {name} because it still has " \
                             "{nb} volumes".format(name=self.name, nb=nb_vols))
        else:
            logging.warn("undefining storage pool {name}".format(name=self.name))
            storage_pool.undefine()

    def create(self):

        """
            Creates the StoragePool in libvirt. If it already exists, simply
            link to it.
        """

        storage_pool = self.ctl.find_storage_pool(self.path)

        if storage_pool is not None:
            logging.info("found storage pool {name} with the same path" \
                             .format(name=storage_pool.name()))
            self.libvirt_name = storage_pool.name() # override libvirt name

            # if not active in libvirt (defined but not started), activate it
            # TODO: virStoragePool.isActive() should be called in VirtController
            if not storage_pool.isActive():
                logging.info("storage pool {name} is not active, activating it..." \
                                 .format(name=self.libvirt_name))
                # TODO: virStoragePool.create() should be called in VirtController
                storage_pool.create(0)

        else:
            self.ctl.create_storage_pool(self.toxml())

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
        node_name = self._doc.createTextNode(self.libvirt_name)
        element_name.appendChild(node_name)
        element_pool.appendChild(element_name)

        # target node
        element_target = self._doc.createElement("target")
        element_pool.appendChild(element_target)

        # path node
        element_path = self._doc.createElement("path")
        node_path = self._doc.createTextNode(self.path)
        element_path.appendChild(node_path)
        element_target.appendChild(element_path)
