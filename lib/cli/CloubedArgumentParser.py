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

""" Cloubed script arguments parser """

from ..CloubedException import CloubedArgumentException
import argparse
import logging

class CloubedArgumentParser(argparse.ArgumentParser):

    def __init__(self, description, **kwargs):

        argparse.ArgumentParser.__init__(self, description, **kwargs)

    def error(self, message):

        #self.print_usage(_sys.stderr)
        #self.exit(2, _('%s: error: %s\n') % (self.prog, message))
        raise CloubedArgumentException(message)

    def parse_args(self):

        self._args = super(CloubedArgumentParser, self).parse_args()

        return self._args

    def add_args(self):

        self.add_argument("actions",
                            nargs=1,
                            choices=['gen', 'boot', 'wait', 'status', 'cleanup'],
                            help="name of the action to perform")

        # TODO: actually still to be implemented
        self.add_argument("-c", "--conf",
                            dest="configuration_filename",
                            default="cloubed.yaml",
                            help="Alternate testbed YAML file (default: " \
                                 "cloubed.yaml)")

        self.add_argument("-d", "--debug",
                            help='Enable debug output',
                            action="store_true")

        self.add_argument("--domain",
                            dest="domain",
                            nargs=1,
                            help="The domain on which the action will be performed",
                            required=False )

        # We create argparse groups of arguments in order to classify parameters by
        # actions in the output of --help. See documentation of argparse module for
        # more details about this feature.
        parser_boot_grp = self.add_argument_group('Arguments for boot action')
        parser_gen_grp = self.add_argument_group('Arguments for gen action')
        parser_wait_grp = self.add_argument_group('Arguments for wait action')

        parser_boot_grp.add_argument("--bootdev",
                            dest='bootdev',
                            nargs='?',
                            choices=['hd', 'network', 'cdrom'],
                            help="Boot device with boot action")

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

    def check_required(self):

        action = self._args.actions[0]

        logging.debug(u"check for required parameters with {action} action" \
                          .format(action=action))

        required_args = {
                "boot": {
                    "domain": "--domain"
                },
                "gen" : {
                    "domain": "--domain"
                },
                "wait": {
                    "domain": "--domain"
                },
                "status": {},
                "cleanup": {}
            }

        error_str = u"{attribute} is required for {action} action"

        for attr, arg in required_args[action].iteritems():
            if not hasattr(self._args, attr) or \
               getattr(self._args, attr) is None:
                raise CloubedArgumentException(
                          error_str.format(attribute=arg,
                                           action=action))

    def check_optionals(self):

        action = self._args.actions[0]

        logging.debug(u"check for incoherent parameters with {action} action" \
                          .format(action=action))

        optional_args = {
                "boot": {
                    "bootdev": "--bootdev",
                    "overwrite_disks": "--overwrite-disks",
                    "recreate_networks": "--recreate-networks"
                },
                "gen" : {
                    "filename": "--filename",
                },
                "wait": {
                     "event": "--event"
                },
                "status": {},
                "cleanup": {}
            }

        error_str = u"{attribute} has no sense with {action} action"

        for action_name, compatible_args in optional_args.iteritems():

            if action_name == action:
                continue # go to next item in optional_args

            for attr, arg in compatible_args.iteritems():
                if hasattr(self._args, attr) and \
                   getattr(self._args, attr) is not None:
                    raise CloubedArgumentException(
                              error_str.format(attribute=arg,
                                               action=action))

    def check_bootdev(self):

        if self._args.bootdev:
            return self._args.bootdev
        else:
            return 'hd' # default value
            # It is not set in parameter of argparse.add_argument(default='hd')
            # because in this case args.bootdev is therefore defined all the
            # times and it raises errors in check_args_coherency() for
            # action != boot
