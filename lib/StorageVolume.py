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

""" StorageVolume class of Cloubed """

import logging
import os
from xml.dom.minidom import Document, parseString

from StoragePool import StoragePool # used in __init__
from CloubedException import CloubedException
from Utils import getuser

class StorageVolume:

    """ StorageVoluem class """

    _storage_volumes = []

    def __init__(self, conn, storage_volume_conf):

        self._conn = conn
        sp_name = storage_volume_conf.get_storage_pool()
        self._storage_pool = StoragePool.get_storage_pool_by_name(sp_name)
        self._virtobj = None
        self._name = storage_volume_conf.get_name()
        use_namespace = True # should better be a conf parameter in the future
        if use_namespace:    # logic should moved be in an abstract parent class
            self._libvirt_name = \
                "{user}:{testbed}:{name}" \
                    .format(user = getuser(),
                            testbed = storage_volume_conf.get_testbed(),
                            name = self._name)
        else:
            self._libvirt_name = self._name
        self._size = storage_volume_conf.get_size()
        self._imgtype = storage_volume_conf.get_format()

        self._doc = None

        StorageVolume._storage_volumes.append(self)

    def __del__(self):

        try:
            StorageVolume._storage_volumes.remove(self)
        except ValueError:
            pass

    def __eq__(self, other): # needed for __del__

        return self._name == other.get_name()

    def __repr__(self):

        return "{name} [{size}GB]".format(name=self._name,
                                          size=self._size)

    @classmethod
    def get_storage_volumes_list(cls):

        """
            get_storage_volumes_list: Returns the list of all existing
                                      StorageVolumes
        """

        return cls._storage_volumes

    @classmethod
    def get_by_name(cls, storage_volume_name):

        """
            get_by_name: Returns the StorageVolume with the name given in
                         parameter
        """

        for storage_volume in cls._storage_volumes:
            if storage_volume.get_name() == storage_volume_name:
                return storage_volume

        # none
        raise CloubedException("storage volume {storage_volume_name} " \
                               "not found in the list of defined storage " \
                               "volume ({list_storage_volumes})" \
                                   .format(storage_volume_name = storage_volume_name,
                                           list_storage_volumes = cls._storage_volumes))

    def xml(self):

        """
            Returns the libvirt XML representation of the StorageVolume
        """

        self.__init_xml()
        return self._doc

    def toxml(self):

        """
            Returns the libvirt XML representation of the StorageVolume as string
        """

        return self.xml().toxml()

    def getfilename(self):

        """
            getfilename: Returns the file name of the StorageVolume
        """

        return self._libvirt_name + "." + self._imgtype

    def getpath(self):

        """
            getpath: Returns the full absolute path of the StorageVolume
        """

        return os.path.join(self._storage_pool.getpath(), self.getfilename())

    def get_name(self):

        """
            get_name: Returns the name of the StorageVolume
        """

        return self._name

    def find_storage_volume(self):

        """
            Search for any storage volue with the same name among all storage
            volumes in Libvirt. If one matches, returns it. Else returns None.
        """

        storage_pool = self._storage_pool.find_storage_pool()

        if storage_pool is not None:

            for storage_volume_name in storage_pool.listVolumes():
                if storage_volume_name == self.getfilename():
                    return storage_pool \
                        .storageVolLookupByName(storage_volume_name)

        return None

    def get_infos(self):
        """
            Returns a dict full of key/value string pairs with information about
            the StorageVolume
        """

        infos = {}

        if self._storage_pool.get_status() == 'undefined':

            infos['status'] = "-"

        else:

            storage_volume = self.find_storage_volume()

            if storage_volume is not None:

                self._virtobj = storage_volume
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

            else:

                infos['status'] = 'undefined'

        return infos

    def getvirtobj(self):

        """
            getvirtobj: Returns the libvirt object of the StorageVolume
        """

        return self._virtobj

    def created(self):

        """
            created: Returns True if the StorageVolume has been created in
                     libvirt
        """

        return self._virtobj is not None

    def destroy(self):

        """
            Destroys the StorageVolume in libvirt
        """

        storage_volume = self.find_storage_volume()

        if storage_volume is None:
            logging.debug("unable to destroy storage volume {name} since not " \
                          "found in libvirt".format(name=self._name))
            return # do nothing and leave

        logging.warn("destroying storage volume {name}".format(name=self._name))
        storage_volume.delete(0)

    def create(self, overwrite = True):

        """
            create: Creates the StorageVolume in libvirt
        """

        self._storage_pool.create()

        found = False
        sv_name = None

        # delete storage volumes w/ the same name
        for sv_name in self._storage_pool.getvirtobj().listVolumes():
            if sv_name == self.getfilename():
                found = True
                break # ends for loop

        if found:
            storage_volume = self._storage_pool \
                                     .getvirtobj() \
                                         .storageVolLookupByName(sv_name)
            if overwrite:
                # first delete then re-create the storage volume
                logging.info("deleting storage volume " + sv_name)
                storage_volume.delete(0)
                self._virtobj = self._storage_pool \
                                        .getvirtobj() \
                                            .createXML(self.toxml(), 0)
            else:
                self._virtobj = storage_volume
        else:
            self._virtobj = self._storage_pool \
                                    .getvirtobj() \
                                        .createXML(self.toxml(), 0)

    def __init_xml(self):

        """
            __init_xml: Generates the libvirt XML representation of the
                        StorageVolume
        """

        self._doc = Document()

        # <volume>
        #   <name>imgname.img</name>
        #   <allocation>0</allocation>
        #   <capacity unit="G">10</capacity>
        #   <target>
        #     <format type='qcow2'/>
        #     <permissions>
        #       <owner>1001</owner>
        #       <group>1000</group>
        #       <mode>0744</mode>
        #       <label>virt_image_t</label>
        #     </permissions>
        #   </target>
        # </volume>

        # root element: volume
        element_volume = self._doc.createElement("volume")
        self._doc.appendChild(element_volume)

        # name element
        element_name = self._doc.createElement("name")
        node_name = self._doc.createTextNode(self.getfilename())
        element_name.appendChild(node_name)
        element_volume.appendChild(element_name)
        
        # allocation element
        element_allocation = self._doc.createElement("allocation")
        node_allocation = self._doc.createTextNode("0")
        element_allocation.appendChild(node_allocation)
        element_volume.appendChild(element_allocation)
        
        # capacity element
        element_capacity = self._doc.createElement("capacity")
        element_capacity.setAttribute("unit", "G") # gigabyte
        node_capacity = self._doc.createTextNode(str(self._size))
        element_capacity.appendChild(node_capacity)
        element_volume.appendChild(element_capacity)

        # target element
        element_target = self._doc.createElement("target")
        element_volume.appendChild(element_target)

        # target/format element
        element_format = self._doc.createElement("format")
        element_format.setAttribute("type", self._imgtype)
        element_target.appendChild(element_format)

        # target/permissions element
        element_permissions = self._doc.createElement("permissions")
        element_target.appendChild(element_permissions)

        # target/permissions/owner element
        #element_owner = self._doc.createElement("owner")
        #node_owner = self._doc.createTextNode("1001")
        #element_owner.appendChild(node_owner)
        #element_permissions.appendChild(element_owner)

        # target/permissions/group element
        #element_group = self._doc.createElement("group")
        #node_group = self._doc.createTextNode("1000")
        #element_group.appendChild(node_group)
        #element_permissions.appendChild(element_group)

        # target/permissions/mode element
        element_mode = self._doc.createElement("mode")
        node_mode = self._doc.createTextNode("0744")
        element_mode.appendChild(node_mode)
        element_permissions.appendChild(element_mode)

        # target/permissions/label element
        element_label = self._doc.createElement("label")
        node_label = self._doc.createTextNode("virt_image_t")
        element_label.appendChild(node_label)
        element_permissions.appendChild(element_label)
