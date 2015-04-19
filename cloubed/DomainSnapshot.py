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

""" DomainSnapshot class of Cloubed """

import os
from xml.dom.minidom import Document

class DomainSnapshot:

    """ DomainSnapshot class """

    def __init__(self, conn, name, storage_volume):

        self._conn = conn
        self._virtobj = None

        self._name = name
        self._storage_volume = storage_volume

        # snapshot root path <- storage volume path without extension
        snapshot_root_path = os.path.splitext(storage_volume.getpath())[0]
 
        self._snapshot_path = "{:s}-snapshot-{:s}.qcow2" \
                                  .format(snapshot_root_path,
                                          self._name)

        self._doc = None

        self.__init_xml()

    def toxml(self):

        """
            toxml: Returns the libvirt XML representation of the DomainSnapshot
        """

        return self._doc.toxml()

    def get_path(self):

        """
            get_path: Returns the path of the DomainSnapshot
        """

        return self._snapshot_path

    def __init_xml(self):

        """
           __init_xml: Generates libvirt XML representation of the
                       DomainSnapshot
        """

        self._doc = Document() 

        # <domainsnapshot>
        #   <description>Snapshot of OS install and updates</description>
        #   <disks>
        #     <disk name='/path/to/old'>
        #       <source file='/path/to/new'/>
        #     </disk>
        #   </disks>
        # </domainsnapshot>

        # root element: domainsnapshot
        element_domainsnapshot = self._doc.createElement("domainsnapshot")
        self._doc.appendChild(element_domainsnapshot)

        # name element
        element_name = self._doc.createElement("name")
        node_name = self._doc.createTextNode(self._name)
        element_name.appendChild(node_name)
        element_domainsnapshot.appendChild(element_name)

        # description element
        element_description = self._doc.createElement("description")
        node_description = self._doc.createTextNode("snapshot {:s}" \
                                                        .format(self._name))
        element_description.appendChild(node_description)
        element_domainsnapshot.appendChild(element_description)

        # disks element
        element_disks = self._doc.createElement("disks")
        element_domainsnapshot.appendChild(element_disks)

        # disks/disk
        element_disk = self._doc.createElement("disk")
        element_disk.setAttribute("name", self._storage_volume.getpath())
        element_disks.appendChild(element_disk)

        # disks/disk/source
        element_source = self._doc.createElement("source")
        element_source.setAttribute("file", self._snapshot_path)
        element_disk.appendChild(element_source)
