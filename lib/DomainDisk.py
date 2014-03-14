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

""" DomainDisk class of Cloubed """

from StorageVolume import StorageVolume

class DomainDisk:

    """ DomainDisk class """

    def __init__(self, device, storage_volume_name):

        self._device = device
        self._storage_volume = StorageVolume.get_by_name(storage_volume_name)

    def get_device(self):

        """ get_device: Returns the device name of the DomainDisk """

        return self._device

    def get_storage_volume(self):

        """ get_storage_volume: Returns the StorageVolume of the DomainDisk """

        return self._storage_volume

    def get_storage_volume_name(self):

        """ Returns the name of the StorageVolume """

        return self._storage_volume.get_name()
