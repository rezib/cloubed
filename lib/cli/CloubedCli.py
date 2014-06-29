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

""" All functions for cloubed CLI script"""

from ..Cloubed import Cloubed
from ..CloubedException import CloubedException, CloubedArgumentException
from ..cli.CloubedArgumentParser import CloubedArgumentParser
import sys
import logging

def print_testbed_infos(testbed):
    """
        Prints nicely a dict full of informations about the testbed and its
        resources, including their status in Libvirt.
    """

    print "storage pools:"
    for name, infos in testbed['storagepools'].iteritems():
        print_storage_pool_infos(name, infos)

    print "storage volumes:"
    for name, infos in testbed['storagevolumes'].iteritems():
        print_storage_volume_infos(name, infos)

    print "networks:"
    for name, infos in testbed['networks'].iteritems():
        print_network_infos(name, infos)

    print "domains:"
    for name, infos in testbed['domains'].iteritems():
        print_domain_infos(name, infos)

def print_storage_pool_infos(name, infos):
    """
        Prints nicely a dict full of informations about a storage pool.
    """

    print "  - {name}".format(name=name)
    for key, value in infos.iteritems():
        print "    - {key:10s}: {value:10s}".format(key=key, value=value)

def print_storage_volume_infos(name, infos):
    """
        Prints nicely a dict full of informations about a storage volume.
    """

    print "  - {name}".format(name=name)
    print "    - status    : {status}".format(status=infos['status'])
    if infos.has_key('path'):
        print "    - path      : {path}".format(path=infos['path'])
    if infos.has_key('allocation') and infos.has_key('capacity'):
        print "    - size      : {allocation:.2f}/{capacity:.2f}GB" \
                  .format(allocation = infos['allocation']/1024,
                          capacity = infos['capacity']/1024)

def print_network_infos(name, infos):
    """
        Prints nicely a dict full of informations about a network.
    """

    print "  - {name}".format(name=name)
    print "    - status    : {status}".format(status=infos['status'])
    if infos.has_key('bridge'):
        print "    - bridge    : {bridge}".format(bridge=infos['bridge'])
    if infos.has_key('ip') and infos.has_key('netmask'):
        print "    - ip        : {ip}/{netmask}" \
                  .format(ip = infos['ip'],
                          netmask = infos['netmask'])

def print_domain_infos(name, infos):
    """
        Prints nicely a dict full of informations about a domain.
    """

    print "  - {name}".format(name=name)
    for key, value in infos.iteritems():
        print "    - {key:10s}: {value:10s}".format(key=key, value=value)

def print_template_vars(domain_vars):
    """Prints the dict of variables that could be used in the templates for a
       domain.

       :param dict domain_vars: the dict of variables that could be used in
           templates for a domain.
    """

    tb_keys = []
    sp_keys = []
    sv_keys = []
    nt_keys = []
    dm_keys = []

    for key in domain_vars.iterkeys():
        if key.startswith('testbed'): tb_keys.append(key)
        elif key.startswith('storagepool'): sp_keys.append(key)
        elif key.startswith('storagevolume'): sv_keys.append(key)
        elif key.startswith('network'): nt_keys.append(key)
        elif key.startswith('domain'): dm_keys.append(key)
        elif key.startswith('self'): dm_keys.append(key)

    for key in sorted(tb_keys):
        print("{key}: {var}".format(key=key, var=domain_vars[key]))
    for key in sorted(sp_keys):
        print("{key}: {var}".format(key=key, var=domain_vars[key]))
    for key in sorted(sv_keys):
        print("{key}: {var}".format(key=key, var=domain_vars[key]))
    for key in sorted(nt_keys):
        print("{key}: {var}".format(key=key, var=domain_vars[key]))
    for key in sorted(dm_keys):
        print("{key}: {var}".format(key=key, var=domain_vars[key]))

def main():

    """ run_cloubed: function launched by main() """

    parser = CloubedArgumentParser(u"cloubed")
    parser.add_args()

    try:
        args = parser.parse_args()

        # enable debug mode
        if args.debug:
            logging.basicConfig(format='%(levelname)-7s: %(message)s',
                                level=logging.DEBUG)

        parser.check_required()
        parser.check_optionals()

        try:
            cloubed = Cloubed()
        except CloubedException as cdb_error:
            # in most cases because yaml file not found
            # TODO: manage this case specifically for a better error message
            logging.error(u"Error while initializing cloubed: {error}" \
                              .format(error=str(cdb_error)))
            sys.exit(1)

        action_name = args.actions[0]

        if action_name == "gen":

            domain_name = args.domain[0]
            filename = args.filename[0]

            logging.debug(u"Action gen on {domain} with template {template}" \
                              .format(domain=domain_name,
                                      template=filename))

            cloubed.gen_file(domain_name, filename)

        elif action_name == u"boot":

            domain_name = args.domain[0]
            disks_to_overwrite = parser.parse_disks()
            networks_to_recreate = parser.parse_networks()
            bootdev = parser.parse_bootdev()

            logging.debug(u"Action boot on {domain}" \
                              .format(domain=domain_name))

            cloubed.boot_vm(domain_name, bootdev,
                            disks_to_overwrite,
                            networks_to_recreate)

        elif action_name == u"wait":

            domain_name = args.domain[0]
            waited_event = parser.parse_event()
            event_type = waited_event[0]
            event_detail = waited_event[1]

            logging.debug(u"Action wait on {domain} with " \
                           "{event_type}/{event_detail}" \
                           .format(domain=domain_name,
                                   event_type=event_type,
                                   event_detail=event_detail))

            cloubed.wait_event(domain_name, event_type, event_detail)

        elif action_name == u"status":

            testbed = cloubed.get_infos()

            print_testbed_infos(testbed)

        elif action_name == u"vars":

            domain_name = args.domain[0]
            domain_vars = cloubed.get_templates_dict(domain_name)
            print_template_vars(domain_vars)

        elif action_name == u"cleanup":

            logging.debug(u"Action cleanup")
            cloubed.cleanup()

        elif action_name == u"xml":

            logging.debug(u"Action xml")
            resource_type, resource_name = parser.parse_resource()
            xml = cloubed.xml(resource_type, resource_name)
            print xml.toprettyxml(indent="  ")

        else:
            raise CloubedArgumentException(
                      u"Unknown action '{action}'".format(action=action_name))

    except CloubedArgumentException as cdb_error:
        logging.error(cdb_error)
        sys.exit(1)
    except CloubedException as cdb_error:
        logging.error(cdb_error)
        sys.exit(1)
    except KeyboardInterrupt:
        logging.info(u"Cloubed stopped.")
