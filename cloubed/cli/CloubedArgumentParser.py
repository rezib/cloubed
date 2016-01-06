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
                            choices=['gen',
                                     'boot',
                                     'shutdown',
                                     'destroy',
                                     'reboot',
                                     'reset',
                                     'suspend',
                                     'resume',
                                     'wait',
                                     'status',
                                     'cleanup',
                                     'vars',
                                     'xml'],
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
        parser_xml_grp = self.add_argument_group('Arguments for xml action')

        parser_boot_grp.add_argument("--bootdev",
                            dest='bootdev',
                            nargs=1,
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

        parser_wait_grp.add_argument("--enable-http",
                            dest='enable_http',
                            help="Enable internal HTTP server",
                            action="store_true")

        parser_xml_grp.add_argument("--resource",
                            dest='resource',
                            nargs=1,
                            help="Print XML description of this resource")


    def check_required(self):

        action = self._args.actions[0]

        logging.debug(u"check for required parameters with {action} action" \
                          .format(action=action))

        required_args = {
                "boot": {
                    "domain": "--domain"
                },
                "shutdown": {
                    "domain": "--domain"
                },
                "destroy": {
                    "domain": "--domain"
                },
                "reboot": {
                    "domain": "--domain"
                },
                "reset": {
                    "domain": "--domain"
                },
                "suspend": {
                    "domain": "--domain"
                },
                "resume": {
                    "domain": "--domain"
                },
                "gen" : {
                    "domain": "--domain",
                    "filename": "--filename"
                },
                "wait": {
                    "domain": "--domain",
                    "event": "--event"
                },
                "status": {},
                "cleanup": {},
                "vars": {
                    "domain": "--domain"
                },
                "xml": {
                    "resource": "--resource"
                }
            }

        error_str = u"{attribute} is required for {action} action"

        for attr, arg in required_args[action].iteritems():
            if not hasattr(self._args, attr) or \
               getattr(self._args, attr) is None:
                raise CloubedArgumentException(
                          error_str.format(attribute=arg,
                                           action=action))

    def check_optionals(self):
        """
            Checks if all defined arguments are compatible with the given
            action
        """

        action = self._args.actions[0]

        logging.debug(u"check for incoherent parameters with {action} action" \
                          .format(action=action))

        # Options that are either systematically defined (ex: with default
        # values, like configuration_filename) or global option not specific to
        # an action (ex: debug). These options will be ignored in the check.
        default_args = ['configuration_filename',
                        'actions',
                        'debug']

        # For each action, list of all compatible options
        action_args = {
            'boot': [ 'domain',
                      'bootdev',
                      'overwrite_disks',
                      'recreate_networks' ],
            'shutdown' : [ 'domain' ],
            'destroy' : [ 'domain' ],
            'reboot' : [ 'domain' ],
            'reset' : [ 'domain' ],
            'suspend' : [ 'domain' ],
            'resume' : [ 'domain' ],
            'gen' : [ 'domain', 'filename' ],
            'wait': [ 'domain', 'event', 'enable_http' ],
            'status': [],
            'cleanup': [],
            'vars': [ 'domain' ],
            'xml': [ 'resource' ]
        }

        # For each argument, the name of the corresponding long option
        options = {
            'domain': '--domain',
            'bootdev': '--bootdev',
            'overwrite_disks': '--overwrite-disks',
            'recreate_networks': '--recreate-networks',
            'filename': '--filename',
            'event': '--event',
            'enable_http': '--enable-http',
            'resource': '--resource'
        }

        error_str = u"{attribute} is not compatible with {action} action"

        # Get list of compatible args
        compatible_args = action_args[action]
        # Loop over the list of defined args
        for arg, value in self._args.__dict__.iteritems():
            if arg not in default_args \
               and value is not None \
               and arg not in compatible_args \
               and type(self._args.__dict__[arg]) is not bool:
                raise CloubedArgumentException(
                          error_str.format(attribute=options[arg],
                                           action=action))

    def parse_bootdev(self):

        if self._args.bootdev:
            return self._args.bootdev[0]
        else:
            return 'hd' # default value
            # It is not set in parameter of argparse.add_argument(default='hd')
            # because in this case args.bootdev is therefore defined all the
            # times and it raises errors in check_args_coherency() for
            # action != boot

    def parse_disks(self):
        """
           Parses and returns values of --overwrite-disks parameter of boot
           action or raises exception if problem is found
        """

        if self._args.overwrite_disks:

            disks = self._args.overwrite_disks

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

                return disks

        else:

            logging.debug(u"--overwrite-disks not defined, defaulting to 'no'")
            return False

    def parse_networks(self):
        """
           Parses and returns values of --recreate-networks parameter of boot
           action or raises exception if problem is found
        """

        if self._args.recreate_networks:

            networks = self._args.recreate_networks

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

                return networks

        else:

            logging.debug(u"--recreate-networks not defined, defaulting to 'no'")
            return False

    def parse_event(self):
        """
           Parses and returns values of --event parameter of wait action or
           raises exception if problem is found
        """

        waited_event_str = self._args.event[0]
        waited_event = waited_event_str.split(':')
        if len(waited_event) is not 2:
            raise CloubedArgumentException(u"format of --event parameter " \
                                            "is not valid")
        return waited_event

    def parse_resource(self):
        """
           Parses and returns values of --resource parameter of xml action or
           raises exception if problem is found
        """

        resource_str = self._args.resource[0]
        resource = resource_str.split(':')
        if len(resource) is not 2:
            raise CloubedArgumentException(u"format of --resource parameter " \
                                            "is not valid")
        return resource
