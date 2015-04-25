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

import logging
import atexit

from cloubed.Cloubed import Cloubed

# It is not actually used in this module but it has to be exported in
# cloubed external API
from cloubed.CloubedException import *

def gen(domain, template):

    """Generates a file for a domain based on template"""

    cloubed = Cloubed()
    cloubed.gen_file(domain, template)

def boot(domain, bootdev="hd",
         overwrite_disks=[],
         recreate_networks=[]):

    """Boot a domain"""

    cloubed = Cloubed()
    cloubed.boot_vm(domain, bootdev, overwrite_disks, recreate_networks)

def create_network(network_name, recreate):

    """ Creates network in libvirt """

    cloubed = Cloubed()
    cloubed.create_network(network_name, recreate)

def cleanup():

    """ Destroys all resources in libvirt """

    cloubed = Cloubed()
    cloubed.cleanup()

def wait(domain, event, detail, enable_http=False):

    """Wait for an event on a domain"""

    cloubed = Cloubed()
    cloubed.wait_event(domain, event, detail, enable_http)

def storage_pools():

    """ Returns the list of storage pools names """

    cloubed = Cloubed()
    return cloubed.storage_pools()

def storage_volumes():

    """ Returns the list of storage volumes names """

    cloubed = Cloubed()
    return cloubed.storage_volumes()

def networks():

    """ Returns the list of networks names """

    cloubed = Cloubed()
    return cloubed.networks()

def domains():

    """ Returns the list of domains names """

    cloubed = Cloubed()
    return cloubed.domains()

def _clean_exit():

    if Cloubed.initialized():
        # get the singleton instance
        cloubed = Cloubed()
        cloubed.clean_exit()

atexit.register(_clean_exit)

#
# Deprecated API functions
#

def gen_file(domain_name, template_name):
    """Deprecated function to generate file for a domain base on template"""

    logging.warning("gen_file() function is deprecated, please use gen() " \
                    "function instead")
    gen(domain_name, template_name)

def boot_vm(domain_name, bootdev="hd",
            overwrite_disks=[],
            recreate_networks=[]):
    """Deprecated functions to boot a domain."""

    logging.warning("boot_vm() function is deprecated, please use boot() " \
                    "function instead")
    boot(domain_name, bootdev, overwrite_disks, recreate_networks)

def wait_event(domain_name, event_type, event_detail, enable_http=False):
    """Deprecated function to wait for an event on a domain"""

    wait(domain_name, event_type, event_detail, enable_http)
