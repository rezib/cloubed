#!/usr/bin/python3

import os

from CloubedTests import *

from cloubed.conf.Configuration import Configuration
from cloubed.conf.ConfigurationNetwork import ConfigurationNetwork
from cloubed.CloubedException import CloubedConfigurationException
from Mock import MockConfigurationLoader, conf_minimal

valid_network_item = { 'name': 'test_network_name' }

class TestConfigurationNetwork(CloubedTestCase):

    def setUp(self):
        self._network_item = valid_network_item
        self._loader = MockConfigurationLoader(conf_minimal)
        self.conf = Configuration(self._loader)
        self.network_conf = ConfigurationNetwork(self.conf, self._network_item)

    def test_get_type(self):
        """
            ConfigurationNetwork._get_type() should return network
        """
        self.assertEqual(self.network_conf._get_type(), 'network')

    def test_get_templates_dict(self):
        """
            ConfigurationNetwork.get_templates_dict() should return a dict
            with all parameters of the network
        """
        self.assertDictContainsSubset(
                 {'network.test_network_name.forward_mode': 'None'},
                 self.network_conf.get_templates_dict())

class TestConfigurationNetworkForwardMode(CloubedTestCase):

    def setUp(self):
        self._network_item = valid_network_item
        self._loader = MockConfigurationLoader(conf_minimal)
        self.conf = Configuration(self._loader)
        self.network_conf = ConfigurationNetwork(self.conf, self._network_item)

    def test_parse_forward_mode_ok(self):
        """
            ConfigurationNetwork.__parse_forward_mode() should parse valid
            values without errors and set _forward_mode instance attribute
        """
        conf = {}
        self.network_conf._ConfigurationNetwork__parse_forward_mode(conf)
        self.assertEqual(self.network_conf.forward_mode, None)

        conf = {'forward': 'nat'}
        self.network_conf._ConfigurationNetwork__parse_forward_mode(conf)
        self.assertEqual(self.network_conf.forward_mode, 'nat')

        conf = {'forward': 'none'}
        self.network_conf._ConfigurationNetwork__parse_forward_mode(conf)
        self.assertEqual(self.network_conf.forward_mode, None)

    def test_parse_forward_mode_not_str(self):
        """
            ConfigurationNetwork.__parse_forward_mode() should raise a
            CloubedConfigurationException if the format of forward parameter in
            the configuration is not valid
        """

        invalid_confs = [ { 'forward': None },
                          { 'forward': 42 },
                          { 'forward': [] } ]

        for invalid_conf in invalid_confs:
            self.assertRaisesRegex(
                     CloubedConfigurationException,
                     "Forward parameter format of network {network} is not " \
                     "valid".format(network=self.network_conf.name),
                     self.network_conf._ConfigurationNetwork__parse_forward_mode,
                     invalid_conf)

    def test_parse_forward_mode_not_valid(self):
        """
            ConfigurationNetwork.__parse_forward_mode() should raise a
            CloubedConfigurationException if the forward parameter in the
            configuration is not valid
        """

        invalid_conf = { 'forward': 'unknown' }

        self.assertRaisesRegex(
                 CloubedConfigurationException,
                 "Forward parameter of network {network} is not valid" \
                     .format(network=self.network_conf.name),
                 self.network_conf._ConfigurationNetwork__parse_forward_mode,
                 invalid_conf)

class TestConfigurationNetworkBridgeName(CloubedTestCase):

    def setUp(self):
        self._network_item = valid_network_item
        self._loader = MockConfigurationLoader(conf_minimal)
        self.conf = Configuration(self._loader)
        self.network_conf = ConfigurationNetwork(self.conf, self._network_item)

    def test_parse_bridge_name_ok(self):
        """
            ConfigurationNetwork.__parse_bridge_name() should parse valid
            values without errors and set bridge_name instance attribute
        """

        conf = { 'forward': 'bridge',
                 'bridge': 'test_bridge_name' }

        self.network_conf._ConfigurationNetwork__parse_forward_mode(conf)
        self.network_conf._ConfigurationNetwork__parse_bridge_name(conf)
        self.assertEqual(self.network_conf.bridge_name,
                         'test_bridge_name')

        conf = { 'forward': 'nat' }
        self.network_conf._ConfigurationNetwork__parse_forward_mode(conf)
        self.network_conf._ConfigurationNetwork__parse_bridge_name(conf)
        self.assertEqual(self.network_conf.bridge_name,
                         None)

    def test_parse_bridge_name_wrong_forward(self):
        """
            ConfigurationNetwork.__parse_forward_mode() should raise a
            CloubedConfigurationException if the bridge parameter is defined
            on a network with forward mode != bridge
        """

        invalid_conf = { 'forward': 'nat',
                         'bridge': 'test_bridge_name' }

        self.network_conf._ConfigurationNetwork__parse_forward_mode(invalid_conf)
        self.assertRaisesRegex(
                 CloubedConfigurationException,
                 "Bridge parameter has no sense on network {network} with " \
                 "forwarding mode nat" \
                     .format(network=self.network_conf.name),
                 self.network_conf._ConfigurationNetwork__parse_bridge_name,
                 invalid_conf)

    def test_parse_bridge_name_missing(self):
        """
            ConfigurationNetwork.__parse_forward_mode() should raise a
            CloubedConfigurationException if the bridge parameter is not defined
            on a network with forward mode == bridge
        """

        invalid_conf = { 'forward': 'bridge' }

        self.network_conf._ConfigurationNetwork__parse_forward_mode(invalid_conf)
        self.assertRaisesRegex(
                 CloubedConfigurationException,
                 "Bridge parameter is missing on network {network} with " \
                 "bridge forwarding mode" \
                     .format(network=self.network_conf.name),
                 self.network_conf._ConfigurationNetwork__parse_bridge_name,
                 invalid_conf)

    def test_parse_bridge_name_invalid_format(self):
        """
            ConfigurationNetwork.__parse_forward_mode() should raise a
            CloubedConfigurationException if the format bridge parameter is not
            valid
        """

        invalid_confs = [ { 'forward': 'bridge', 'bridge': []   },
                          { 'forward': 'bridge', 'bridge': 42   },
                          { 'forward': 'bridge', 'bridge': None } ]

        for invalid_conf in invalid_confs:
            self.network_conf._ConfigurationNetwork__parse_forward_mode(invalid_conf)
            self.assertRaisesRegex(
                 CloubedConfigurationException,
                 "Bridge parameter format of network {network} is not valid" \
                     .format(network=self.network_conf.name),
                 self.network_conf._ConfigurationNetwork__parse_bridge_name,
                 invalid_conf)

class TestConfigurationNetworkIpHostNetmask(CloubedTestCase):

    def setUp(self):
        self._network_item = valid_network_item
        self._loader = MockConfigurationLoader(conf_minimal)
        self.conf = Configuration(self._loader)
        self.network_conf = ConfigurationNetwork(self.conf, self._network_item)

    def test_parse_ip_host_netmask_ok(self):
        """
            ConfigurationNetwork.__parse_ip_host_netmask() should parse valid
            values without errors and set ip_host and netmask instance
            attributes properly
        """

        conf = { 'address': '10.0.0.1/24' }
        self.network_conf._ConfigurationNetwork__parse_forward_mode(conf)
        self.network_conf._ConfigurationNetwork__parse_ip_host_netmask(conf)
        self.assertEqual(self.network_conf.ip_host, '10.0.0.1')
        self.assertEqual(self.network_conf.netmask, '255.255.255.0')

        # old deprecated parameters
        conf = { 'ip_host': '10.0.0.1',
                 'netmask': '255.255.255.0' }
        self.network_conf._ConfigurationNetwork__parse_forward_mode(conf)
        self.network_conf._ConfigurationNetwork__parse_ip_host_netmask(conf)
        self.assertEqual(self.network_conf.ip_host, '10.0.0.1')
        self.assertEqual(self.network_conf.netmask, '255.255.255.0')

        # in this case ConfigurationNetwork.has_local_settings() should also
        # return True
        self.assertEqual(self.network_conf.has_local_settings(), True)

        conf = { }
        self.network_conf._ConfigurationNetwork__parse_forward_mode(conf)
        self.network_conf._ConfigurationNetwork__parse_ip_host_netmask(conf)
        self.assertEqual(self.network_conf.ip_host, None)
        self.assertEqual(self.network_conf.netmask, None)

        # in this case ConfigurationNetwork.has_local_settings() should also
        # return False
        self.assertEqual(self.network_conf.has_local_settings(), False)

    def test_parse_address_bridge_mode(self):
        """
            ConfigurationNetwork.__parse_ip_host_netmask() should raise
            CloubedConfigurationException if address is set on network in
            bridge forwarding mode
        """

        invalid_conf = { 'forward': 'bridge',
                         'address': '10.0.0.1/24' }
        self.network_conf._ConfigurationNetwork__parse_forward_mode(invalid_conf)
        self.assertRaisesRegex(
             CloubedConfigurationException,
             "address parameter has no sense on network {network} with " \
             "bridge forwarding mode" \
                 .format(network=self.network_conf.name),
             self.network_conf._ConfigurationNetwork__parse_ip_host_netmask,
             invalid_conf)
    def test_parse_ip_host_netmask_bridge_mode(self):
        """
            ConfigurationNetwork.__parse_ip_host_netmask() should raise
            CloubedConfigurationException if ip_host and netmask are set
            on network in bridge forwarding mode
        """

        invalid_conf = { 'forward': 'bridge',
                         'ip_host': '10.0.0.1',
                         'netmask': '255.255.255.0' }
        self.network_conf._ConfigurationNetwork__parse_forward_mode(invalid_conf)
        self.assertRaisesRegex(
             CloubedConfigurationException,
             "ip_host and netmask parameters have no sense on network " \
             "{network} with bridge forwarding mode" \
                 .format(network=self.network_conf.name),
             self.network_conf._ConfigurationNetwork__parse_ip_host_netmask,
             invalid_conf)

    def test_parse_ip_host_netmask_no_netmask(self):
        """
            ConfigurationNetwork.__parse_ip_host_netmask() should raise
            CloubedConfigurationException if ip_host is set without netmask
        """

        invalid_conf = { 'ip_host': '10.0.0.1' }
        self.network_conf._ConfigurationNetwork__parse_forward_mode(invalid_conf)
        self.assertRaisesRegex(
             CloubedConfigurationException,
             "ip_host cannot be set without netmask parameter on network " \
             "{network}" \
                 .format(network=self.network_conf.name),
             self.network_conf._ConfigurationNetwork__parse_ip_host_netmask,
             invalid_conf)

    def test_parse_ip_host_netmask_no_ip_host(self):
        """
            ConfigurationNetwork.__parse_ip_host_netmask() should raise
            CloubedConfigurationException if netmask is set without ip_host
        """

        invalid_conf = { 'netmask': '255.255.255.0' }
        self.network_conf._ConfigurationNetwork__parse_forward_mode(invalid_conf)
        self.assertRaisesRegex(
             CloubedConfigurationException,
             "netmask cannot be set without ip_host parameter on network " \
             "{network}" \
                 .format(network=self.network_conf.name),
             self.network_conf._ConfigurationNetwork__parse_ip_host_netmask,
             invalid_conf)

    def test_parse_ip_host_address_invalid_format(self):
        """
            ConfigurationNetwork.__parse_ip_host_netmask() should raise
            CloubedConfigurationException if the format of the address
            parameter is not valid
        """

        invalid_conf = { 'address': [] }
        self.network_conf._ConfigurationNetwork__parse_forward_mode(invalid_conf)
        self.assertRaisesRegex(
             CloubedConfigurationException,
             "address parameter format on network {network} is not valid" \
                 .format(network=self.network_conf.name),
             self.network_conf._ConfigurationNetwork__parse_ip_host_netmask,
             invalid_conf)

    def test_parse_ip_host_netmask_invalid_format(self):
        """
            ConfigurationNetwork.__parse_ip_host_netmask() should raise
            CloubedConfigurationException if the formats of the ip_host and
            netmask parameters are not valid
        """

        invalid_conf = { 'ip_host': [], 'netmask': 'str' }
        self.network_conf._ConfigurationNetwork__parse_forward_mode(invalid_conf)
        self.assertRaisesRegex(
             CloubedConfigurationException,
             "ip_host parameter format on network {network} is not valid" \
                 .format(network=self.network_conf.name),
             self.network_conf._ConfigurationNetwork__parse_ip_host_netmask,
             invalid_conf)

        invalid_conf = { 'ip_host': 'str', 'netmask': 42 }
        self.network_conf._ConfigurationNetwork__parse_forward_mode(invalid_conf)
        self.assertRaisesRegex(
             CloubedConfigurationException,
             "netmask parameter format on network {network} is not valid" \
                 .format(network=self.network_conf.name),
             self.network_conf._ConfigurationNetwork__parse_ip_host_netmask,
             invalid_conf)

    def test_parse_ip_host_address_invalid_value(self):
        """
            ConfigurationNetwork.__parse_ip_host_netmask() should raise
            CloubedConfigurationException if the value of address parameter
            is not a valid network address in CIDR syntax
        """

        invalid_confs = [ { 'address': 'fail'           },
                          { 'address': '192.168.0.1/35' },
                          { 'address': '260.0.0.0/24'   } ]

        for invalid_conf in invalid_confs:

            self.network_conf._ConfigurationNetwork__parse_forward_mode(invalid_conf)
            self.assertRaisesRegex(
                 CloubedConfigurationException,
                 "address parameter on network {network} is not a valid " \
                 "network address".format(network=self.network_conf.name),
                 self.network_conf._ConfigurationNetwork__parse_ip_host_netmask,
                 invalid_conf)

    def test_parse_ip_host_netmask_invalid_addresss(self):
        """
            ConfigurationNetwork.__parse_ip_host_netmask() should raise
            CloubedConfigurationException if the type of ip_host and netmask
            parameters are not respectively valid IPv4 address and netmask
        """

        invalid_conf = { 'ip_host': 'fail', 'netmask': '255.255.255.0' }
        self.network_conf._ConfigurationNetwork__parse_forward_mode(invalid_conf)
        self.assertRaisesRegex(
             CloubedConfigurationException,
             "ip_host parameter on network {network} is not a valid IPv4 " \
             "address" \
                 .format(network=self.network_conf.name),
             self.network_conf._ConfigurationNetwork__parse_ip_host_netmask,
             invalid_conf)

        invalid_conf = { 'ip_host': '10.0.0.1', 'netmask': 'fail' }
        self.network_conf._ConfigurationNetwork__parse_forward_mode(invalid_conf)
        self.assertRaisesRegex(
             CloubedConfigurationException,
             "netmask parameter on network {network} is not a valid IPv4 " \
             "netmask" \
                 .format(network=self.network_conf.name),
             self.network_conf._ConfigurationNetwork__parse_ip_host_netmask,
             invalid_conf)

class TestConfigurationNetworkDhcp(CloubedTestCase):

    def setUp(self):
        self._network_item = valid_network_item
        self._loader = MockConfigurationLoader(conf_minimal)
        self.conf = Configuration(self._loader)
        self.network_conf = ConfigurationNetwork(self.conf, self._network_item)

    def test_parse_dhcp_ok(self):
        """
            ConfigurationNetwork.__parse_dhcp() should parse valid values
            without errors and set dhcp_start and dhcp_end instance attributes
            properly
        """

        conf = { 'ip_host': '10.0.0.1',
                 'netmask': '255.255.255.0' }
        self.network_conf._ConfigurationNetwork__parse_forward_mode(conf)
        self.network_conf._ConfigurationNetwork__parse_ip_host_netmask(conf)

        conf = { 'dhcp':
                     { 'start': '10.0.0.100',
                       'end'  : '10.0.0.200' } }
        self.network_conf._ConfigurationNetwork__parse_dhcp(conf)
        self.assertEqual(self.network_conf.dhcp_start, '10.0.0.100')
        self.assertEqual(self.network_conf.dhcp_end, '10.0.0.200')

        # in this case ConfigurationNetwork.has_dhcp() should also return True
        self.assertEqual(self.network_conf.has_dhcp(), True)

        conf = { }
        self.network_conf._ConfigurationNetwork__parse_dhcp(conf)
        self.assertEqual(self.network_conf.dhcp_start, None)
        self.assertEqual(self.network_conf.dhcp_end, None)

        # in this case ConfigurationNetwork.has_dhcp() should also return False
        self.assertEqual(self.network_conf.has_dhcp(), False)

    def test_parse_dhcp_no_ip_host(self):
        """
            ConfigurationNetwork.__parse_dhcp() should raise 
            CloubedConfigurationException if dhcp parameters are set on a
            network without ip_host/netmask
        """
        invalid_conf = { 'dhcp':
                             { 'start': '10.0.0.100',
                               'end'  : '10.0.0.200' } }
        self.network_conf._ConfigurationNetwork__parse_forward_mode(invalid_conf)
        self.network_conf._ConfigurationNetwork__parse_ip_host_netmask(invalid_conf)
        self.assertRaisesRegex(
             CloubedConfigurationException,
             "dhcp service cannot be set-up on network {network} without " \
             "ip_host and netmask" \
                 .format(network=self.network_conf.name),
             self.network_conf._ConfigurationNetwork__parse_dhcp,
             invalid_conf)

    def test_parse_dhcp_missing_parameter(self):
        """
            ConfigurationNetwork.__parse_dhcp() should raise 
            CloubedConfigurationException if there is any missing parameter in
            dhcp section of the network
        """
        invalid_conf = { 'ip_host': '10.0.0.1',
                         'netmask': '255.255.255.0',
                         'dhcp':
                             { 'start': '10.0.0.100' } }
        self.network_conf._ConfigurationNetwork__parse_forward_mode(invalid_conf)
        self.network_conf._ConfigurationNetwork__parse_ip_host_netmask(invalid_conf)
        self.assertRaisesRegex(
             CloubedConfigurationException,
             "end parameter must be defined in dhcp section of network " \
             "{network}" \
                 .format(network=self.network_conf.name),
             self.network_conf._ConfigurationNetwork__parse_dhcp,
             invalid_conf)

    def test_parse_dhcp_invalid_format(self):
        """
            ConfigurationNetwork.__parse_dhcp() should raise 
            CloubedConfigurationException if the format of any parameter in the
            dhcp section is not valid
        """
        invalid_conf = { 'ip_host': '10.0.0.1',
                         'netmask': '255.255.255.0',
                         'dhcp':
                             { 'start': '10.0.0.100',
                               'end': 42 } }
        self.network_conf._ConfigurationNetwork__parse_forward_mode(invalid_conf)
        self.network_conf._ConfigurationNetwork__parse_ip_host_netmask(invalid_conf)
        self.assertRaisesRegex(
             CloubedConfigurationException,
             "end parameter format in dhcp section of network {network} is " \
             "not valid" \
                 .format(network=self.network_conf.name),
             self.network_conf._ConfigurationNetwork__parse_dhcp,
             invalid_conf)

    def test_parse_dhcp_invalid_address(self):
        """
            ConfigurationNetwork.__parse_dhcp() should raise 
            CloubedConfigurationException if the format of any parameter in the
            dhcp section is not valid
        """
        invalid_conf = { 'ip_host': '10.0.0.1',
                         'netmask': '255.255.255.0',
                         'dhcp':
                             { 'start': '10.0.0.100',
                               'end': 'fail' } }
        self.network_conf._ConfigurationNetwork__parse_forward_mode(invalid_conf)
        self.network_conf._ConfigurationNetwork__parse_ip_host_netmask(invalid_conf)
        self.assertRaisesRegex(
             CloubedConfigurationException,
             "end parameter in dhcp section of network {network} is not a " \
             "valid IPv4 address" \
                 .format(network=self.network_conf.name),
             self.network_conf._ConfigurationNetwork__parse_dhcp,
             invalid_conf)

class TestConfigurationNetworkDomain(CloubedTestCase):

    def setUp(self):
        self._network_item = valid_network_item
        self._loader = MockConfigurationLoader(conf_minimal)
        self.conf = Configuration(self._loader)
        self.network_conf = ConfigurationNetwork(self.conf, self._network_item)

    def test_parse_domain_ok(self):
        """
            ConfigurationNetwork.__parse_domain() should parse valid values
            without errors and set domain instance attribute properly
        """

        conf = { 'ip_host': '10.0.0.1',
                 'netmask': '255.255.255.0',
                 'dhcp':
                     { 'start': '10.0.0.100',
                       'end'  : '10.0.0.200' } }
        self.network_conf._ConfigurationNetwork__parse_forward_mode(conf)
        self.network_conf._ConfigurationNetwork__parse_ip_host_netmask(conf)
        self.network_conf._ConfigurationNetwork__parse_dhcp(conf)

        conf = { 'domain': 'test_domain' }
        self.network_conf._ConfigurationNetwork__parse_domain(conf)
        self.assertEqual(self.network_conf.domain, 'test_domain')

        conf = { }
        self.network_conf._ConfigurationNetwork__parse_domain(conf)
        self.assertEqual(self.network_conf.domain, None)

    def test_parse_domain_no_dhcp(self):
        """
            ConfigurationNetwork.__parse_domain() should raise
            CloubedConfigurationException if domain parameter is set on a
            network without dhcp
        """
        invalid_conf = { 'ip_host': '10.0.0.1',
                         'netmask': '255.255.255.0',
                         'domain': 'test_domain' }
        self.network_conf._ConfigurationNetwork__parse_forward_mode(invalid_conf)
        self.network_conf._ConfigurationNetwork__parse_ip_host_netmask(invalid_conf)
        self.network_conf._ConfigurationNetwork__parse_dhcp(invalid_conf)
        self.assertRaisesRegex(
             CloubedConfigurationException,
             "domain parameter cannot be set-up on network {network} without dhcp" \
                 .format(network=self.network_conf.name),
             self.network_conf._ConfigurationNetwork__parse_domain,
             invalid_conf)

    def test_parse_domain_invalid_format(self):
        """
            ConfigurationNetwork.__parse_domain() should raise
            CloubedConfigurationException if the format of the domain parameter
            is not valid
        """
        invalid_conf = { 'ip_host': '10.0.0.1',
                         'netmask': '255.255.255.0',
                         'dhcp':
                             { 'start': '10.0.0.100',
                               'end'  : '10.0.0.200' },
                         'domain': 42 }
        self.network_conf._ConfigurationNetwork__parse_forward_mode(invalid_conf)
        self.network_conf._ConfigurationNetwork__parse_ip_host_netmask(invalid_conf)
        self.network_conf._ConfigurationNetwork__parse_dhcp(invalid_conf)
        self.assertRaisesRegex(
             CloubedConfigurationException,
             "format of domain parameter of network {network} is not valid" \
                 .format(network=self.network_conf.name),
             self.network_conf._ConfigurationNetwork__parse_domain,
             invalid_conf)

class TestConfigurationNetworkPxe(CloubedTestCase):

    def setUp(self):
        self._network_item = valid_network_item
        self._loader = MockConfigurationLoader(conf_minimal)
        self.conf = Configuration(self._loader)
        self.network_conf = ConfigurationNetwork(self.conf, self._network_item)

    def test_parse_pxe_ok(self):
        """
            ConfigurationNetwork.__parse_pxe() should parse valid values
            without errors and set pxe_tftp_dir and pxe_boot_file instance
            attributes properly
        """

        conf = { 'ip_host': '10.0.0.1',
                 'netmask': '255.255.255.0',
                 'dhcp':
                     { 'start': '10.0.0.100',
                       'end'  : '10.0.0.200' } }
        self.network_conf._ConfigurationNetwork__parse_forward_mode(conf)
        self.network_conf._ConfigurationNetwork__parse_ip_host_netmask(conf)
        self.network_conf._ConfigurationNetwork__parse_dhcp(conf)

        conf = { 'pxe': '/test_tftp_dir/test_boot_file' }
        self.network_conf._ConfigurationNetwork__parse_pxe(conf)
        self.assertEqual(self.network_conf.pxe_tftp_dir, '/test_tftp_dir')
        self.assertEqual(self.network_conf.pxe_boot_file, 'test_boot_file')

        conf = { 'pxe': 'test_tftp_dir/test_boot_file' }
        self.network_conf._ConfigurationNetwork__parse_pxe(conf)
        self.assertEqual(self.network_conf.pxe_tftp_dir,
                         os.path.join(os.getcwd(),"test_tftp_dir"))
        self.assertEqual(self.network_conf.pxe_boot_file, 'test_boot_file')

        conf = { 'pxe': 'test_boot_file' }
        self.network_conf._ConfigurationNetwork__parse_pxe(conf)
        self.assertEqual(self.network_conf.pxe_tftp_dir, os.getcwd())
        self.assertEqual(self.network_conf.pxe_boot_file, 'test_boot_file')

        conf = { 'pxe':
                     { 'tftp_dir': '/test_tftp_dir', # absolute path
                       'boot_file': 'test_boot_file' } }
        self.network_conf._ConfigurationNetwork__parse_pxe(conf)
        self.assertEqual(self.network_conf.pxe_tftp_dir, '/test_tftp_dir')
        self.assertEqual(self.network_conf.pxe_boot_file, 'test_boot_file')

        # in this case ConfigurationNetwork.has_pxe() should also return True
        self.assertEqual(self.network_conf.has_pxe(), True)

        conf = { 'pxe':
                     { 'tftp_dir': 'test_tftp_dir', # relative path
                       'boot_file': 'test_boot_file' } }
        self.network_conf._ConfigurationNetwork__parse_pxe(conf)
        self.assertEqual(self.network_conf.pxe_tftp_dir,
                         os.path.join(os.getcwd(),"test_tftp_dir"))
        self.assertEqual(self.network_conf.pxe_boot_file, 'test_boot_file')

        conf = { } 
        self.network_conf._ConfigurationNetwork__parse_pxe(conf)
        self.assertEqual(self.network_conf.pxe_tftp_dir, None)
        self.assertEqual(self.network_conf.pxe_boot_file, None)

        # in this case ConfigurationNetwork.has_pxe() should also return False
        self.assertEqual(self.network_conf.has_pxe(), False)

    def test_parse_pxe_no_dhcp(self):
        """
            ConfigurationNetwork.__parse_pxe() should raise 
            CloubedConfigurationException if pxe parameters are set on a
            network without dhcp
        """
        invalid_conf = { 'ip_host': '10.0.0.1',
                         'netmask': '255.255.255.0',
                         'pxe': 'test_tftp_dir/test_boot_file' }
        self.network_conf._ConfigurationNetwork__parse_forward_mode(invalid_conf)
        self.network_conf._ConfigurationNetwork__parse_ip_host_netmask(invalid_conf)
        self.network_conf._ConfigurationNetwork__parse_dhcp(invalid_conf)
        self.assertRaisesRegex(
             CloubedConfigurationException,
             "pxe service cannot be set-up on network {network} without dhcp" \
                 .format(network=self.network_conf.name),
             self.network_conf._ConfigurationNetwork__parse_pxe,
             invalid_conf)

    def test_parse_pxe_invalid_format(self):
        """
            ConfigurationNetwork.__parse_pxe() should raise
            CloubedConfigurationException if pxe parameter has an invalid format
        """
        invalid_conf = { 'ip_host': '10.0.0.1',
                         'netmask': '255.255.255.0',
                         'dhcp':
                             { 'start': '10.0.0.100',
                               'end'  : '10.0.0.200' },
                         'pxe': 42 }
        self.network_conf._ConfigurationNetwork__parse_forward_mode(invalid_conf)
        self.network_conf._ConfigurationNetwork__parse_ip_host_netmask(invalid_conf)
        self.network_conf._ConfigurationNetwork__parse_dhcp(invalid_conf)
        self.assertRaisesRegex(
             CloubedConfigurationException,
             "format of pxe parameter of network {network} is not valid" \
                 .format(network=self.network_conf.name),
             self.network_conf._ConfigurationNetwork__parse_pxe,
             invalid_conf)

    def test_parse_pxe_missing_boot_file(self):
        """
            ConfigurationNetwork.__parse_pxe() should raise
            CloubedConfigurationException if pxe parameter has a missing boot
            file
        """
        invalid_conf = { 'ip_host': '10.0.0.1',
                         'netmask': '255.255.255.0',
                         'dhcp':
                             { 'start': '10.0.0.100',
                               'end'  : '10.0.0.200' },
                         'pxe': 'test_tftp_dir/' }
        self.network_conf._ConfigurationNetwork__parse_forward_mode(invalid_conf)
        self.network_conf._ConfigurationNetwork__parse_ip_host_netmask(invalid_conf)
        self.network_conf._ConfigurationNetwork__parse_dhcp(invalid_conf)
        self.assertRaisesRegex(
             CloubedConfigurationException,
             "pxe parameter of network {network} must specify a boot file" \
                 .format(network=self.network_conf.name),
             self.network_conf._ConfigurationNetwork__parse_pxe,
             invalid_conf)

    def test_parse_pxe_missing_parameter(self):
        """
            ConfigurationNetwork.__parse_pxe() should raise 
            CloubedConfigurationException if one parameter is missing in the pxe
            dict of a network
        """
        invalid_conf = { 'ip_host': '10.0.0.1',
                         'netmask': '255.255.255.0',
                         'dhcp':
                             { 'start': '10.0.0.100',
                               'end'  : '10.0.0.200' },
                         'pxe':
                             { 'tftp_dir': 'test_tftp_dir' } }
        self.network_conf._ConfigurationNetwork__parse_forward_mode(invalid_conf)
        self.network_conf._ConfigurationNetwork__parse_ip_host_netmask(invalid_conf)
        self.network_conf._ConfigurationNetwork__parse_dhcp(invalid_conf)
        self.assertRaisesRegex(
             CloubedConfigurationException,
             "boot_file parameter must be defined in pxe section of network " \
             "{network}" \
                 .format(network=self.network_conf.name),
             self.network_conf._ConfigurationNetwork__parse_pxe,
             invalid_conf)

    def test_parse_pxe_invalid_format_parameter(self):
        """
            ConfigurationNetwork.__parse_pxe() should raise 
            CloubedConfigurationException if pxe parameters are set on a
            network without dhcp
        """
        invalid_conf = { 'ip_host': '10.0.0.1',
                         'netmask': '255.255.255.0',
                         'dhcp':
                             { 'start': '10.0.0.100',
                               'end'  : '10.0.0.200' },
                         'pxe':
                             { 'tftp_dir': 'test_tftp_dir',
                               'boot_file': 42 } }
        self.network_conf._ConfigurationNetwork__parse_forward_mode(invalid_conf)
        self.network_conf._ConfigurationNetwork__parse_ip_host_netmask(invalid_conf)
        self.network_conf._ConfigurationNetwork__parse_dhcp(invalid_conf)
        self.assertRaisesRegex(
             CloubedConfigurationException,
             "boot_file parameter format in pxe section of network {network} " \
             "is not valid" \
                 .format(network=self.network_conf.name),
             self.network_conf._ConfigurationNetwork__parse_pxe,
             invalid_conf)

loadtestcase(TestConfigurationNetwork)
loadtestcase(TestConfigurationNetworkForwardMode)
loadtestcase(TestConfigurationNetworkBridgeName)
loadtestcase(TestConfigurationNetworkIpHostNetmask)
loadtestcase(TestConfigurationNetworkDhcp)
loadtestcase(TestConfigurationNetworkDomain)
loadtestcase(TestConfigurationNetworkPxe)
