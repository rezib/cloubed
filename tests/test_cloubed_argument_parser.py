#!/usr/bin/env python

import sys

from CloubedTests import *
from lib.cli.CloubedArgumentParser import CloubedArgumentParser
from lib.CloubedException import CloubedArgumentException

class TestCloubedArgumentParser(CloubedTestCase):

    def setUp(self):
        pass

    def test_parse_args_no_action(self):
        """
            Raises CloubedArgumentException because too few arguments
        """
        sys.argv = ["cloubed"]
        parser = CloubedArgumentParser(u"test_description")
        parser.add_args()
        self.assertRaisesRegexp(CloubedArgumentException,
                                "too few arguments",
                                parser.parse_args)

    def test_parse_args_invalid_action(self):
        """
            Raises CloubedArgumentException because invalid action
        """
        sys.argv = ["cloubed", "badaction"]
        parser = CloubedArgumentParser(u"test_description")
        parser.add_args()
        self.assertRaisesRegexp(CloubedArgumentException,
                                "argument actions: invalid choice:",
                                parser.parse_args)

    def test_parse_args_config_noarg(self):
        """
            Raises CloubedArgumentException because conf expects argument
        """
        sys.argv = ["cloubed", "boot", "--conf"]
        parser = CloubedArgumentParser(u"test_description")
        parser.add_args()
        self.assertRaisesRegexp(CloubedArgumentException,
                                "argument -c/--conf: expected one argument",
                                parser.parse_args)

    def test_parse_args_domain_noarg(self):
        """
            Raises CloubedArgumentException because domain expects argument
        """
        sys.argv = ["cloubed", "boot", "--domain"]
        parser = CloubedArgumentParser(u"test_description")
        parser.add_args()
        self.assertRaisesRegexp(CloubedArgumentException,
                                "argument --domain: expected 1 argument\(s\)",
                                parser.parse_args)

    def test_parse_args_unrecognized_arg(self):
        """
            Raises CloubedArgumentException because unrecognized argument
        """
        sys.argv = ["cloubed", "boot", "--domain", "toto", "--toto"]
        parser = CloubedArgumentParser(u"test_description")
        parser.add_args()
        self.assertRaisesRegexp(CloubedArgumentException,
                                "unrecognized arguments: --toto",
                                parser.parse_args)

    def test_parse_args_bootdev_noarg(self):
        """
            Raises CloubedArgumentException because bootdev expects argument
        """
        sys.argv = ["cloubed", "boot", "--domain", "toto", "--bootdev"]
        parser = CloubedArgumentParser(u"test_description")
        parser.add_args()
        self.assertRaisesRegexp(CloubedArgumentException,
                                "argument --bootdev: expected 1 argument\(s\)",
                                parser.parse_args)

    def test_parse_args_invalid_bootdev(self):
        """
            Raises CloubedArgumentException because invalid bootdev
        """
        sys.argv = ["cloubed", "boot", "--domain", "toto", "--bootdev", "toto"]
        parser = CloubedArgumentParser(u"test_description")
        parser.add_args()
        self.assertRaisesRegexp(CloubedArgumentException,
                                "argument --bootdev: invalid choice:",
                                parser.parse_args)

    def test_parse_args_overwritedisks_noarg(self):
        """
            Raises CloubedArgumentException because overwrite disks expects
            argument
        """
        sys.argv = ["cloubed", "boot", "--domain", "toto", "--overwrite-disks"]
        parser = CloubedArgumentParser(u"test_description")
        parser.add_args()
        self.assertRaisesRegexp(CloubedArgumentException,
                                "argument --overwrite-disks: expected at least one argument",
                                parser.parse_args)

    def test_parse_args_recreatenetworks_noarg(self):
        """
            Raises CloubedArgumentException because recreate networks expects
            argument
        """
        sys.argv = ["cloubed", "boot", "--domain", "toto", "--recreate-networks"]
        parser = CloubedArgumentParser(u"test_description")
        parser.add_args()
        self.assertRaisesRegexp(CloubedArgumentException,
                                "argument --recreate-networks: expected at least one argument",
                                parser.parse_args)

    def test_parse_args_filename_noarg(self):
        """
            Raises CloubedArgumentException because filename expects argument
        """
        sys.argv = ["cloubed", "boot", "--domain", "toto", "--filename"]
        parser = CloubedArgumentParser(u"test_description")
        parser.add_args()
        self.assertRaisesRegexp(CloubedArgumentException,
                                "argument --filename: expected 1 argument\(s\)",
                                parser.parse_args)
    
    def test_parse_args_event_noarg(self):
        """
            Raises CloubedArgumentException because event expects argument
        """
        sys.argv = ["cloubed", "wait", "--domain", "toto", "--event"]
        parser = CloubedArgumentParser(u"test_description")
        parser.add_args()
        self.assertRaisesRegexp(CloubedArgumentException,
                                "argument --event: expected 1 argument\(s\)",
                                parser.parse_args)

    #
    # CloubedArgumentParser.check_required()
    #

    def test_check_required_action_no_domain(self):
        """
            Raises CloubedArgumentException because action requires domain
        """
        actions = [ "boot", "gen", "wait", "vars" ]
        for action in actions:
            sys.argv = ["cloubed", action]
            parser = CloubedArgumentParser(u"test_description")
            parser.add_args()
            parser.parse_args()
            self.assertRaisesRegexp(CloubedArgumentException,
                                    "--domain is required for {action} action" \
                                        .format(action=action),
                                    parser.check_required)

    def test_check_required_wait_no_event(self):
        """
            Raises CloubedArgumentException because action wait requires event
        """
        sys.argv = ['cloubed', 'wait', '--domain', 'domain']
        parser = CloubedArgumentParser(u"test_description")
        parser.add_args()
        parser.parse_args()
        self.assertRaisesRegexp(CloubedArgumentException,
                                "--event is required for wait action",
                                parser.check_required)

    def test_check_required_action_no_arg(self):
        """
            Does not raise CloubedArgumentException because no required args
            for these actions
        """
        actions = [ "status", "cleanup" ]
        for action in actions:
            sys.argv = ["cloubed", action]
            parser = CloubedArgumentParser(u"test_description")
            parser.add_args()
            parser.parse_args()
            parser.check_required()

    #
    # CloubedArgumentParser.check_optionals()
    #

    def test_arg_coherency_boot_filename(self):
        """
            Raises CloubedArgumentException because filename nonsense with boot
            action
        """
        sys.argv = ["cloubed", "boot", "--domain", "toto", "--filename", "toto"]
        parser = CloubedArgumentParser(u"test_description")
        parser.add_args()
        parser.parse_args()
        self.assertRaisesRegexp(CloubedArgumentException,
                                "--filename is not compatible with boot action",
                                parser.check_optionals)

    def test_arg_coherency_boot_event(self):
        """
            Raises CloubedArgumentException because event nonsense with boot
            action
        """
        sys.argv = ["cloubed", "boot", "--domain", "toto", "--event", "toto"]
        parser = CloubedArgumentParser(u"test_description")
        parser.add_args()
        parser.parse_args()
        self.assertRaisesRegexp(CloubedArgumentException,
                                "--event is not compatible with boot action",
                                parser.check_optionals)

    def test_arg_coherency_gen_bootdev(self):
        """
            Raises CloubedArgumentException because event nonsense with boot
            action
        """
        sys.argv = ["cloubed", "gen", "--domain", "toto", "--bootdev", "hd"]
        parser = CloubedArgumentParser(u"test_description")
        parser.add_args()
        parser.parse_args()
        self.assertRaisesRegexp(CloubedArgumentException,
                                "--bootdev is not compatible with gen action",
                                parser.check_optionals)

    def test_arg_coherency_gen_overwritedisks(self):
        """
            Raises CloubedArgumentException because overwrite disks nonsense
            with boot action
        """
        sys.argv = ["cloubed", "gen", "--domain", "toto", "--overwrite-disks", "toto"]
        parser = CloubedArgumentParser(u"test_description")
        parser.add_args()
        parser.parse_args()
        self.assertRaisesRegexp(CloubedArgumentException,
                                "--overwrite-disks is not compatible with gen action",
                                parser.check_optionals)

    def test_arg_coherency_gen_recreatenetworks(self):
        """
            Raises CloubedArgumentException because recreate networks nonsense
            with boot action
        """
        sys.argv = ["cloubed", "gen", "--domain", "toto", "--recreate-networks", "toto"]
        parser = CloubedArgumentParser(u"test_description")
        parser.add_args()
        parser.parse_args()
        self.assertRaisesRegexp(CloubedArgumentException,
                                "--recreate-networks is not compatible with gen action",
                                parser.check_optionals)

    def test_arg_coherency_gen_event(self):
        """
            Raises CloubedArgumentException because event nonsense with boot
            action
        """
        sys.argv = ["cloubed", "gen", "--domain", "toto", "--event", "toto"]
        parser = CloubedArgumentParser(u"test_description")
        parser.add_args()
        parser.parse_args()
        self.assertRaisesRegexp(CloubedArgumentException,
                                "--event is not compatible with gen action",
                                parser.check_optionals)

    def test_arg_coherency_wait_bootdev(self):
        """
            Raises CloubedArgumentException because bootdev nonsense with wait
            action
        """
        sys.argv = ["cloubed", "wait", "--domain", "toto", "--bootdev", "hd"]
        parser = CloubedArgumentParser(u"test_description")
        parser.add_args()
        parser.parse_args()
        self.assertRaisesRegexp(CloubedArgumentException,
                                "--bootdev is not compatible with wait action",
                                parser.check_optionals)

    def test_arg_coherency_wait_overwritedisks(self):
        """
            Raises CloubedArgumentException because overwrite disks nonsense
            with wait action
        """
        sys.argv = ["cloubed", "wait", "--domain", "toto", "--overwrite-disks", "toto"]
        parser = CloubedArgumentParser(u"test_description")
        parser.add_args()
        parser.parse_args()
        self.assertRaisesRegexp(CloubedArgumentException,
                                "--overwrite-disks is not compatible with wait action",
                                parser.check_optionals)

    def test_arg_coherency_wait_recreatenetworks(self):
        """
            Raises CloubedArgumentException because recreate networks nonsense
            with wait action
        """
        sys.argv = ["cloubed", "wait", "--domain", "toto", "--recreate-networks", "toto"]
        parser = CloubedArgumentParser(u"test_description")
        parser.add_args()
        parser.parse_args()
        self.assertRaisesRegexp(CloubedArgumentException,
                                "--recreate-networks is not compatible with wait action",
                                parser.check_optionals)

    def test_arg_coherency_wait_filename(self):
        """
            Raises CloubedArgumentException because filename nonsense with wait
            action
        """
        sys.argv = ["cloubed", "wait", "--domain", "toto", "--filename", "toto"]
        parser = CloubedArgumentParser(u"test_description")
        parser.add_args()
        parser.parse_args()
        self.assertRaisesRegexp(CloubedArgumentException,
                                "--filename is not compatible with wait action",
                                parser.check_optionals)

    #
    # CloubedArgumentParser.parse_bootdev()
    #

    def test_parse_bootdev_explicit(self):
        """
            Checks CloubedArgumentParser.parse_bootdev() returns explicit
            bootdev
        """
        sys.argv = ["cloubed", "boot", "--domain", "toto", "--bootdev", "network"]
        parser = CloubedArgumentParser(u"test_description")
        parser.add_args()
        parser.parse_args()
        self.assertEqual(parser.parse_bootdev(), "network")

    def test_parse_bootdev_implicit_default(self):
        """
            Checks CloubedArgumentParser.parse_bootdev() returns default
            implicit bootdev
        """
        sys.argv = ["cloubed", "boot", "--domain", "toto"]
        parser = CloubedArgumentParser(u"test_description")
        parser.add_args()
        parser.parse_args()
        self.assertEqual(parser.parse_bootdev(), "hd")

    #
    # CloubedArgumentParser.parse_disks()
    #

    def test_parse_disks_default(self):
        """
            Checks CloubedArgumentParser.parse_disks() returns default value
            False
        """
        sys.argv = ['cloubed', 'boot', '--domain', 'toto']
        parser = CloubedArgumentParser(u'test_description')
        parser.add_args()
        parser.parse_args()
        self.assertEqual(parser.parse_disks(), False)

    def test_parse_disks_values(self):
        """
            Checks CloubedArgumentParser.parse_disks() returns the list of given
            disk names if values are valid
        """
        sys.argv = ['cloubed', 'boot', '--domain', 'toto',
                    '--overwrite-disks', 'disk1', 'disk2']
        parser = CloubedArgumentParser(u'test_description')
        parser.add_args()
        parser.parse_args()
        self.assertEqual(parser.parse_disks(), ['disk1', 'disk2'])

    def test_parse_disks_yes_no(self):
        """
            Checks CloubedArgumentParser.parse_disks() returns True if parameter
            value is yes and False if no
        """

        expected_values = { 'yes': True, 'no': False }
        for param, value in expected_values.items():
            sys.argv = ['cloubed', 'boot', '--domain', 'toto',
                        '--overwrite-disks', param]
            parser = CloubedArgumentParser(u'test_description')
            parser.add_args()
            parser.parse_args()
            self.assertEqual(parser.parse_disks(), value)

    def test_parse_disks_yes_no_and_other(self):
        """
            Checks CloubedArgumentParser.parse_disks() raises
            CloubedArgumentException if value yes and no among other disks names
        """
        values = ['yes', 'no']
        for value in values:
            sys.argv = ['cloubed', 'boot', '--domain', 'toto',
                        '--overwrite-disks', value, 'other']
            parser = CloubedArgumentParser(u'test_description')
            parser.add_args()
            parser.parse_args()
            self.assertRaisesRegexp(CloubedArgumentException,
                                    "--overwrite-disks parameter cannot " \
                                    "contain '{value}' among other values" \
                                        .format(value=value),
                                    parser.parse_disks)

    #
    # CloubedArgumentParser.parse_networks()
    #

    def test_parse_networks_default(self):
        """
            Checks CloubedArgumentParser.parse_networks() returns default value
            False
        """
        sys.argv = ['cloubed', 'boot', '--domain', 'toto']
        parser = CloubedArgumentParser(u'test_description')
        parser.add_args()
        parser.parse_args()
        self.assertEqual(parser.parse_networks(), False)

    def test_parse_networks_values(self):
        """
            Checks CloubedArgumentParser.parse_networks() returns the list of
            given networks names if valid values
        """
        sys.argv = ['cloubed', 'boot', '--domain', 'toto',
                    '--recreate-networks', 'network1', 'network2']
        parser = CloubedArgumentParser(u'test_description')
        parser.add_args()
        parser.parse_args()
        self.assertEqual(parser.parse_networks(),
                         ['network1', 'network2'])

    def test_parse_networks_yes_no(self):
        """
            Checks CloubedArgumentParser.parse_networks() returns True if parameter
            value is yes and False if no
        """

        expected_values = { 'yes': True, 'no': False }
        for param, value in expected_values.items():
            sys.argv = ['cloubed', 'boot', '--domain', 'toto',
                        '--recreate-networks', param]
            parser = CloubedArgumentParser(u'test_description')
            parser.add_args()
            parser.parse_args()
            self.assertEqual(parser.parse_networks(), value)

    def test_parse_networks_yes_no_and_other(self):
        """
            Checks CloubedArgumentParser.parse_networks() raises
            CloubedArgumentException if value yes and no among other network
            names
        """
        values = ['yes', 'no']
        for value in values:
            sys.argv = ['cloubed', 'boot', '--domain', 'toto',
                        '--recreate-networks', value, 'other']
            parser = CloubedArgumentParser(u'test_description')
            parser.add_args()
            parser.parse_args()
            self.assertRaisesRegexp(CloubedArgumentException,
                                    "--recreate-networks parameter cannot " \
                                    "contain '{value}' among other values" \
                                        .format(value=value),
                                    parser.parse_networks)

    #
    # CloubedArgumentParser.parse_event()
    #

    def test_parse_event_ok(self):
        """
            Checks CloubedArgumentParser.parse_event() should return a list with
            the 2 parts of the event name
        """
        sys.argv = ['cloubed', 'wait', '--domain', 'toto', '--event', 'part1:part2']
        parser = CloubedArgumentParser(u'test_description')
        parser.add_args()
        parser.parse_args()
        self.assertEquals(parser.parse_event(),
                          ['part1','part2'])

    def test_parse_event_not_valid(self):
        """
            Checks CloubedArgumentParser.parse_event() should raise
            CloubedArgumentException if the format of the event name is not
            valid
        """
        sys.argv = ['cloubed', 'wait', '--domain', 'toto', '--event', 'fail']
        parser = CloubedArgumentParser(u'test_description')
        parser.add_args()
        parser.parse_args()
        self.assertRaisesRegexp(CloubedArgumentException,
                                "format of --event parameter is not valid",
                                parser.parse_event)

    #
    # CloubedArgumentParser.parse_resource()
    #

    def test_parse_resource_ok(self):
        """
            Checks CloubedArgumentParser.parse_resource() should return a list
            with the 2 parts of the resource
        """
        sys.argv = ['cloubed', 'xml', '--resource', 'part1:part2']
        parser = CloubedArgumentParser(u'test_description')
        parser.add_args()
        parser.parse_args()
        self.assertEquals(parser.parse_resource(),
                          ['part1','part2'])

    def test_parse_resource_not_valid(self):
        """
            Checks CloubedArgumentParser.parse_resource() shoudl raise
            CloubedArgumentException if the format of the resource name is not
            valid
        """
        sys.argv = ['cloubed', 'xml', '--resource', 'fail']
        parser = CloubedArgumentParser(u'test_description')
        parser.add_args()
        parser.parse_args()
        self.assertRaisesRegexp(CloubedArgumentException,
                                "format of --resource parameter is not valid",
                                parser.parse_resource)

loadtestcase(TestCloubedArgumentParser)
