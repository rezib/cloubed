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
from xml.dom.minidom import Document

from cloubed.Utils import getuser

class StorageVolume:

    """ StorageVoluem class """

    def __init__(self, tbd, storage_volume_conf):

        self.tbd = tbd
        self.ctl = self.tbd.ctl

        sp_name = storage_volume_conf.storage_pool
        self.storage_pool = self.tbd.get_storage_pool_by_name(sp_name)
        self.name = storage_volume_conf.name
        use_namespace = True # should better be a conf parameter in the future
        if use_namespace:    # logic should moved be in an abstract parent class
            self.libvirt_name = \
                "{user}:{testbed}:{name}" \
                    .format(user = getuser(),
                            testbed = storage_volume_conf.testbed,
                            name = self.name)
        else:
            self.libvirt_name = self.name

        self._size = storage_volume_conf.size
        self._imgtype = storage_volume_conf.format

        self._backing = storage_volume_conf.backing

        self._doc = None

    def __repr__(self):

        return "{name} [{size}GB]".format(name=self.name,
                                          size=self._size)

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

        return self.libvirt_name + "." + self._imgtype

    def getpath(self):

        """
            getpath: Returns the full absolute path of the StorageVolume
        """

        return os.path.join(self.storage_pool.path, self.getfilename())

    def get_infos(self):
        """Returns a dict full of key/value string pairs with information about
           the StorageVolume.
        """
        return self.ctl.info_storage_volume(self.storage_pool,
                                            self.getfilename())

    def destroy(self):

        """
            Destroys the StorageVolume in libvirt
        """

        storage_volume = self.ctl.find_storage_volume(self.storage_pool,
                                                      self.getfilename())

        if storage_volume is None:
            logging.debug("unable to destroy storage volume {name} since not " \
                          "found in libvirt".format(name=self.name))
            return # do nothing and leave

        logging.warn("destroying storage volume {name}".format(name=self.name))
        storage_volume.delete(0)

    def create(self, overwrite=True):

        """
            create: Creates the StorageVolume in libvirt
        """

        found = False
        sv_name = None

        # delete storage volumes w/ the same name
        storage_volume = self.ctl.find_storage_volume(self.storage_pool,
                                                      self.getfilename())
        found = storage_volume is not None

        if found and overwrite:

            # first delete then re-create the storage volume
            logging.info("deleting storage volume {filename}" \
                             .format(filename=self.getfilename()))
            storage_volume.delete(0)
            self.ctl.create_storage_volume(self.storage_pool,
                                           self.toxml())
        elif not found:
            self.ctl.create_storage_volume(self.storage_pool,
                                           self.toxml())

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
        #       <mode>0744</mode>
        #       <label>virt_image_t</label>
        #     </permissions>
        #   </target>
        #   <backingStore>
        #     <path>/home/rpalancher/Documents/git/examples-cloubed/debian/pool/rpalancher:debian:debian-vol-server.qcow2</path>
        #     <permissions>
        #       <mode>0744</mode>
        #       <label>virt_image_t</label>
        #     </permissions>
        #   </backingStore>
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

        #   <backingStore>
        #     <path>/home/rpalancher/Documents/git/examples-cloubed/debian/pool/rpalancher:debian:debian-vol-server.qcow2</path>
        #     <permissions>
        #       <owner>107</owner>
        #       <group>107</group>
        #       <mode>0744</mode>
        #       <label>virt_image_t</label>
        #     </permissions>
        #   </backingStore>

        if self._backing is not None:

            backing = self.tbd.get_storage_volume_by_name(self._backing)

            # backingStore element
            element_backing = self._doc.createElement("backingStore")
            element_volume.appendChild(element_backing)

            # backingStore/path element
            element_path = self._doc.createElement("path")
            node_path = self._doc.createTextNode(backing.getpath())
            element_path.appendChild(node_path)
            element_backing.appendChild(element_path)

            # backingStore/format element
            element_format = self._doc.createElement("format")
            element_format.setAttribute("type", backing._imgtype)
            element_backing.appendChild(element_format)

            # backingStore/permissions element
            element_permissions = self._doc.createElement("permissions")
            element_backing.appendChild(element_permissions)

            # backingStore/permissions/mode element
            element_mode = self._doc.createElement("mode")
            node_mode = self._doc.createTextNode("0744")
            element_mode.appendChild(node_mode)
            element_permissions.appendChild(element_mode)

            # backingStore/permissions/label element
            element_label = self._doc.createElement("label")
            node_label = self._doc.createTextNode("virt_image_t")
            element_label.appendChild(node_label)
            element_permissions.appendChild(element_label)
