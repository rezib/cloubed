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
from DomainEvent import DomainEvent
from CloubedException import CloubedException

def gen_file(domain_name, template_name):

    """ gen_file: """

    cloubed = Cloubed()

    templates_dict = cloubed.get_templates_dict()

    domain = cloubed.get_domain_by_name(domain_name)
    domain_template = domain.get_template_by_name(template_name)
    domain_template.render(templates_dict)

def boot_vm(domain_name, bootdev = "hd", overwrite_disks = [], recreate_networks = []):

    """ boot_vm: """

    cloubed = Cloubed()

    domain = cloubed.get_domain_by_name(domain_name)
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
    cloubed.serve_http()

def wait_event(domain_name, event_type, event_detail):

    """ wait_event: """

    cloubed = Cloubed()

    domain_event = DomainEvent("{event_type}" \
                               .format(event_type=event_type.upper()),
                               "{event_type}_{event_detail}" \
                               .format(event_type=event_type.upper(),
                                       event_detail=event_detail.upper()))
    domain = cloubed.get_domain_by_name(domain_name)
    domain.wait_for_event(domain_event)
