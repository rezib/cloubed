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

""" cloubed module with Cloubed external API"""

import libvirt
import logging

from Cloubed import Cloubed

# It is not actually used in this module but it has to be exported in
# cloubed external API
from CloubedException import CloubedException

def gen_file(domain_name, template_name):

    """ gen_file: """

    cloubed = Cloubed()
    cloubed.gen_file(domain_name, template_name)

def boot_vm(domain_name, bootdev = "hd", overwrite_disks = [], recreate_networks = []):

    """ boot_vm: """

    cloubed = Cloubed()
    cloubed.boot_vm(domain_name, bootdev, overwrite_disks, recreate_networks)

def wait_event(domain_name, event_type, event_detail):

    """ wait_event: """

    cloubed = Cloubed()
    cloubed.wait_event(domain_name, event_type, event_detail)

