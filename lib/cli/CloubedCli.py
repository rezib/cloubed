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
from cloubed.CloubedException import CloubedException
import argparse
import sys
import logging

# TODO: wait ssh and cleanup

def parse_args():
    
    parser = argparse.ArgumentParser(
                 description=u"Perform action over your virtual testbed" )

    parser.add_argument("actions",
                        metavar="ACTION",
                        nargs=1,
                        choices=['gen', 'boot', 'wait'],
                        help="name of the action to perform")

    # TODO: actually still to be implemented
    parser.add_argument("-c", "--conf",
                        dest="configuration_filename",
                        default="cloubed.yaml",
                        help="Alternate testbed YAML file (default: " \
                             "cloubed.yaml)")

    parser.add_argument("-d", "--debug",
                        help='Enable debug output',
                        action="store_true")

    parser.add_argument("--domain",
                        dest='domain',
                        nargs=1,
                        help="The domain on which the action will be performed",
                        required=True )

    # We create argparse groups of arguments in order to classify parameters by
    # actions in the output of --help. See documentation of argparse module for
    # more details about this feature.
    parser_boot_grp = parser.add_argument_group('Arguments for boot action')
    parser_gen_grp = parser.add_argument_group('Arguments for gen action')
    parser_wait_grp = parser.add_argument_group('Arguments for wait action')

    parser_boot_grp.add_argument("--bootdev",
                        dest='bootdev',
                        nargs='?',
                        choices=['hd', 'network', 'cdrom'],
                        help="Boot device with boot action")

    parser_boot_grp.add_argument("--wait-event",
                        dest="waited_event",
                        nargs=1,
                        help="Wait for an event before returning with boot action",)

    parser_boot_grp.add_argument("--overwrite-disks",
                        dest='overwrite_disks',
                        nargs='+',
                        help="Overwrite storage volume with boot action" \
                             " (default: no, possible values are: yes, no or" \
                             " a list of disks separated by blank spaces)")

    parser_boot_grp.add_argument("--recreate-networks",
                        dest='recreate_networks',
                        nargs='+',
                        help="Recreate networks with boot action (default: no," \
                             " possible values are: yes, no or a list of networks" \
                             " separated by blank spaces)")

    parser_gen_grp.add_argument("--filename",
                        dest='filename',
                        nargs=1,
                        help="Template file name to generate")

    parser_wait_grp.add_argument("--event",
                        dest='event',
                        nargs=1,
                        help="Event to wait")

    args = parser.parse_args()

    return parser, args

def check_args_coherency(parser, args):

    action = args.actions[0]

    logging.debug(u"check for incoherent parameters in action {action}" \
                      .format(action=action))

    error_str = u"{attribute} has no sense with {action} action"

    if action == "boot":

        # for gen
        if args.filename:
            parser.error(error_str.format(attribute="--filename",
                                          action=action))
        # for wait
        if args.event:
            parser.error(error_str.format(attribute="--event", action=action))

    elif action == "gen":

        # for boot
        if args.bootdev:
            parser.error(error_str.format(attribute="--bootdev",
                                          action=action))
        if args.waited_event:
            parser.error(error_str.format(attribute="--wait-event",
                                          action=action))
        if args.overwrite_disks:
            parser.error(error_str.format(attribute="--overwrite-disks",
                                          action=action))
        if args.recreate_networks:
            parser.error(error_str.format(attribute="--recreate-networks",
                                          action=action))
        # for wait
        if args.event:
            parser.error(error_str.format(attribute="--event", action=action))

    elif action == "wait":

        # for boot
        if args.bootdev:
            parser.error(error_str.format(attribute="--bootdev",
                                          action=action))
        if args.waited_event:
            parser.error(error_str.format(attribute="--wait-event",
                                          action=action))
        if args.overwrite_disks:
            parser.error(error_str.format(attribute="--overwrite-disks",
                                          action=action))
        if args.recreate_networks:
            parser.error(error_str.format(attribute="--recreate-networks",
                                          action=action))
        # for gen
        if args.filename:
            parser.error(error_str.format(attribute="--filename",
                                          action=action))
def check_disks(cloubed, args):

    if args.overwrite_disks:

        disks = args.overwrite_disks
       
        if "yes" in disks:

            if len(disks)>1:
                logging.error(u"--overwrite-disks parameter cannot contain" \
                                  " 'yes' among other values")
                sys.exit(1)
            else:
                return True

        elif "no" in disks:

            if len(disks)>1:
                logging.error(u"--overwrite-disks parameter cannot contain" \
                                  " 'no' among other values")
                sys.exit(1)
            else:
                return False

        else:

            # check if all disks are declared in YAML file for this domain
            domain_disks_list = [disk.get_storage_volume().get_name() \
                                     for disk in domain.get_disks()]
            for disk in disks:
                if disk not in domain_disks_list:
                    logging.error(u"disk {disk} not found for domain {domain}" \
                                      " in YAML file" \
                                      .format(disk=disk, domain=domain_name)) 
                    sys.exit(1)
            return disks

    else:

        logging.debug(u"--overwrite-disks not defined, defaulting to 'no'")
        return False

def check_networks(cloubed, args):

    if args.recreate_networks:

        networks = args.recreate_networks

        if "yes" in networks:

            if len(networks)>1:
                logging.error(u"--recreate-networks parameter cannot contain" \
                                  " 'yes' among other values")
                sys.exit(1)
            else:
                return True

        elif "no" in networks:

            if len(networks)>1:
                logging.error(u"--recreate-networks parameter cannot contain" \
                                  " 'no' among other values")
                sys.exit(1)
            else:
                return False

        else:

            # check if all networks are declared in YAML file for this domain
            domain_networks_list = [netif.get_network().get_name() \
                                     for netif in domain.get_netifs()]
            for network in networks:
                if network not in domain_networks_list:
                    logging.error(u"network {network} not found for domain" \
                                      " {domain} in YAML file" \
                                      .format(network=network,
                                              domain=domain_name))
                    sys.exit(1)
            return networks

    else:

        logging.debug(u"--recreate-networks not defined, defaulting to 'no'")
        return False

def check_event(cloubed, args):

    if args.waited_event:

        waited_event_str = args.waited_event[0]
        waited_event = waited_event_str.split(':')
        if len(waited_event) is not 2:
            logging.error(u"Badly formated --wait-event parameter, should" \
                              " respect format <event_type>:<event_detail>")
            sys.exit(1)
        return waited_event
    else:

        logging.debug(u"--wait-event parameter not specified")
        return None

def check_bootdev(args):

    if args.bootdev:
        return args.bootdev
    else:
        return 'hd' # default value
        # It is not set in parameter of argparse.add_ergument(default='hd')
        # because in this case args.bootdev is therefore defined all the times
        # and it raises errors in check_args_coherency() for action != boot

def main():

    """ run_cloubed: function launched by main() """

    parser, args = parse_args()

    # enable debug mode
    if args.debug:
        logging.basicConfig(format='%(levelname)-7s: %(message)s',
                            level=logging.DEBUG)

    check_args_coherency(parser, args)

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

         try:
             cloubed.gen_file(domain_name, filename)
         except CloubedException as cdb_error:
             logging.error(cdb_error)
         except KeyboardInterrupt:
             logging.info(u"Cloubed stopped.")

    elif action_name == u"boot":

         domain_name = args.domain[0]
         disks_to_overwrite = check_disks(cloubed, args)
         networks_to_recreate = check_networks(cloubed, args)
         waited_event = check_event(cloubed, args)
         bootdev = check_bootdev(args)

         logging.debug(u"Action boot on {domain}" \
                           .format(domain=domain_name))

         try:
             cloubed.boot_vm(domain_name, bootdev,
                             disks_to_overwrite,
                             networks_to_recreate)
         except CloubedException as cdb_error:
             logging.error(cdb_error)
             sys.exit(1)

         if waited_event is not None:
             event_type = waited_event[0]
             event_detail = waited_event[1]
             try:
                 cloubed.wait_event(domain_name, event_type, event_detail)
             except CloubedException as cdb_error:
                 logging.error(cdb_error)
             except KeyboardInterrupt:
                 logging.info(u"Cloubed stopped.")

    elif action_name == u"wait":

         domain = args.actions[1]
         event_type = args.actions[2]
         event_detail = args.actions[3]

         logging.debug(u"Action wait on {domain} with " \
                           "{event_type}/{event_detail}" \
                           .format(domain=domain,
                                   event_type=event_type,
                                   event_detail=event_detail))
         try:
             cloubed.wait_event(domain, event_type, event_detail)
         except CloubedException as cdb_error:
             logging.error(cdb_error)
         except KeyboardInterrupt:
             logging.info(u"Cloubed stopped.")

    else:

        logging.error(u"Unknown action '{action}'".format(action=action_name))
        sys.exit(1)
