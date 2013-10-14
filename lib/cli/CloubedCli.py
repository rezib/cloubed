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

from cloubed.Cloubed import Cloubed
from cloubed.CloubedException import CloubedException, CloubedArgumentException
from cloubed.cli.CloubedArgumentParser import CloubedArgumentParser
import sys
import logging

def check_disks(cloubed, args):

    if args.overwrite_disks:

        disks = args.overwrite_disks

        if "yes" in disks:

            if len(disks)>1:
                raise CloubedArgumentException(u"--overwrite-disks parameter" \
                                  " cannot contain 'yes' among other values")
            else:
                return True

        elif "no" in disks:

            if len(disks)>1:
                raise CloubedArgumentException(u"--overwrite-disks parameter" \
                                  " cannot contain 'no' among other values")
            else:
                return False

        else:

            # check if all disks are declared in YAML file for this domain
            domain_disks_list = [disk.get_storage_volume().get_name() \
                                     for disk in domain.get_disks()]
            for disk in disks:
                if disk not in domain_disks_list:
                    raise CloubedArgumentException(u"disk {disk} not found for"\
                              " domain {domain} in YAML file" \
                                                    .format(disk=disk,
                                                            domain=domain_name))
            return disks

    else:

        logging.debug(u"--overwrite-disks not defined, defaulting to 'no'")
        return False

def check_networks(cloubed, args):

    if args.recreate_networks:

        networks = args.recreate_networks

        if "yes" in networks:

            if len(networks)>1:
                raise CloubedArgumentException(u"--recreate-networks" \
                                  " parameter cannot contain 'yes' among" \
                                  " other values")
            else:
                return True

        elif "no" in networks:

            if len(networks)>1:
                raise CloubedArgumentException(u"--recreate-networks" \
                                  " parameter cannot contain 'no' among" \
                                  " other values")
            else:
                return False

        else:

            # check if all networks are declared in YAML file for this domain
            domain_networks_list = [netif.get_network().get_name() \
                                     for netif in domain.get_netifs()]
            for network in networks:
                if network not in domain_networks_list:
                    raise CloubedArgumentException(
                              u"network {network} not found for domain {domain}" \
                               "in YAML file".format(network=network,
                                                     domain=domain_name))
            return networks

    else:

        logging.debug(u"--recreate-networks not defined, defaulting to 'no'")
        return False

def check_event(cloubed, args):

    if args.event:

        waited_event_str = args.event[0]
        waited_event = waited_event_str.split(':')
        if len(waited_event) is not 2:
            raise CloubedArgumentException(u"Badly formated --event" \
                      " parameter, should respect format" \
                      " <event_type>:<event_detail>")
        return waited_event
    else:

        logging.debug(u"--event parameter not specified")
        return None

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
             disks_to_overwrite = check_disks(cloubed, args)
             networks_to_recreate = check_networks(cloubed, args)
             bootdev = parser.check_bootdev()

             logging.debug(u"Action boot on {domain}" \
                               .format(domain=domain_name))

             cloubed.boot_vm(domain_name, bootdev,
                             disks_to_overwrite,
                             networks_to_recreate)

        elif action_name == u"wait":

             domain_name = args.domain[0]
             waited_event = check_event(cloubed, args)
             event_type = waited_event[0]
             event_detail = waited_event[1]

             logging.debug(u"Action wait on {domain} with " \
                            "{event_type}/{event_detail}" \
                            .format(domain=domain_name,
                                    event_type=event_type,
                                    event_detail=event_detail))

             cloubed.wait_event(domain_name, event_type, event_detail)

        elif action_name == u"status":

             print "storage pools:"
             for name, status in cloubed.get_storagepools_statuses().iteritems():
                 print "  - {name:30s} {status:10s}".format(name=name, status=status)
             print "storage volumes:"
             for name, status in cloubed.get_storagevolumes_statuses().iteritems():
                 print "  - {name:30s} {status:10s}".format(name=name, status=status)
             print "networks:"
             for name, status in cloubed.get_networks_statuses().iteritems():
                 print "  - {name:30s} {status:10s}".format(name=name, status=status)
             print "domains:"
             for name, status in cloubed.get_domains_statuses().iteritems():
                 print "  - {name:30s} {status:10s}".format(name=name, status=status)

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
