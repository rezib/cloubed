#!/usr/bin/env python

import sys

from CloubedTests import *
from lib.cli.CloubedArgumentParser import CloubedArgumentParser
from lib.cli.CloubedCli import check_disks, \
                               check_networks, \
                               check_event
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
        # FIXME: not raised yet
        #self.assertRaisesRegexp(CloubedArgumentException,
        #                        "argument --bootdev: invalid choice:",
        #                        parser.parse_args)

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
        sys.argv = ["cloubed", "boot", "--domain", "toto", "--event"]
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
        actions = [ "boot", "gen", "wait" ]
        for action in actions:
            sys.argv = ["cloubed", action]
            parser = CloubedArgumentParser(u"test_description")
            parser.add_args()
            parser.parse_args()
            self.assertRaisesRegexp(CloubedArgumentException,
                                    "--domain is required for {action} action" \
                                        .format(action=action),
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
                                "--filename has no sense with boot action",
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
                                "--event has no sense with boot action",
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
                                "--bootdev has no sense with gen action",
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
                                "--overwrite-disks has no sense with gen action",
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
                                "--recreate-networks has no sense with gen action",
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
                                "--event has no sense with gen action",
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
                                "--bootdev has no sense with wait action",
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
                                "--overwrite-disks has no sense with wait action",
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
                                "--recreate-networks has no sense with wait action",
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
                                "--filename has no sense with wait action",
                                parser.check_optionals)

    #
    # CloubedArgumentParser.check_bootdev()
    #

    def test_check_bootdev_explicit(self):
        """
            Checks CloubedArgumentParser.check_bootdev() returns explicit
            bootdev
        """
        sys.argv = ["cloubed", "boot", "--domain", "toto", "--bootdev", "network"]
        parser = CloubedArgumentParser(u"test_description")
        parser.add_args()
        parser.parse_args()
        self.assertEqual(parser.check_bootdev(), "network")

    def test_check_bootdev_implicit_default(self):
        """
            Checks CloubedArgumentParser.check_bootdev() returns default
            implicit bootdev
        """
        sys.argv = ["cloubed", "boot", "--domain", "toto"]
        parser = CloubedArgumentParser(u"test_description")
        parser.add_args()
        parser.parse_args()
        self.assertEqual(parser.check_bootdev(), "hd")

    # invalid wait event with check_event()
    # invalid overwrite disks with check_disks()
    # invalid recreate networks with check_networks()

loadtestcase(TestCloubedArgumentParser)
