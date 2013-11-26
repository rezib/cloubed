#!/usr/bin/env python

from CloubedTests import *

from lib.conf.ConfigurationDomain import ConfigurationDomain
from lib.CloubedException import CloubedConfigurationException

valid_domain_item = { 'name': 'test_name',
                      'testbed': 'test_testbed',
                      'cpu': 2,
                      'memory': 1,
                      'netifs': [
                          { 'network': 'test_netif',
                            'ip': '10.0.0.1' } ],
                      'disks': [
                          { 'device': 'test_device',
                            'storage_volume': 'test_storage_volume' } ] }

class TestConfigurationDomain(CloubedTestCase):

    """ Test all accessors against valid and basic domain dict """

    def setUp(self):
        self._domain_item = valid_domain_item
        self.domain_conf = ConfigurationDomain(self._domain_item)

    def test_get_type(self):
        """
            ConfigurationDomain._get_type() should return domain
        """
        self.assertEqual(self.domain_conf._get_type(), 'domain')

    def test_get_cpu(self):
        """
            ConfigurationDomain.get_cpu() should return the cpu of the domain
        """
        self.assertEqual(self.domain_conf.get_cpu(),
                         2)

    def test_get_memory(self):
        """
            ConfigurationDomain.get_memory() should return the memory size of
            the domain (in MB)
        """
        self.assertEqual(self.domain_conf.get_memory(),
                         1024)

    def test_get_templates_list(self):
        """
            ConfigurationDomain.get_templates_list() should return the list of
            templates of the domain
        """
        self.assertEqual(self.domain_conf.get_templates_list(),
                         [])

    def test_get_netifs_list(self):
        """
            ConfigurationDomain.get_netifs_list() should return the list of
            netifs of the domain
        """
        self.assertEqual(self.domain_conf.get_netifs_list(),
                         [{ 'network': 'test_netif', 'ip': '10.0.0.1' }])

    def test_get_disks_dict(self): 
        """
            ConfigurationDomain.get_disks_dict() should return a dict with all
            disks of the domain
        """
        self.assertEqual(self.domain_conf.get_disks_dict(),
                         { 'test_device': 'test_storage_volume' })

class TestConfigurationDomainCpu(CloubedTestCase):

    def setUp(self):
        self._domain_item = valid_domain_item
        self.domain_conf = ConfigurationDomain(self._domain_item)

    def test_parse_cpu_missing(self):
        """
            ConfigurationDomain.__parse_cpu() should raise
            CloubedConfigurationException when the cpu parameter is missing
        """

        invalid_config = { }
        self.assertRaisesRegexp(
                 CloubedConfigurationException,
                 "cpu parameter of domain test_name is missing",
                 self.domain_conf._ConfigurationDomain__parse_cpu,
                 invalid_config)

    def test_parse_cpu_invalid(self):
        """
            ConfigurationDomain.__parse_cpu() should raise
            CloubedConfigurationException when invalid cpu if given in
            parameter
        """

        invalid_configs = [ { 'cpu': 'x'  },
                            { 'cpu': {}   },
                            { 'cpu': None } ]

        for invalid_config in invalid_configs:
            self.assertRaisesRegexp(
                     CloubedConfigurationException,
                     "format of cpu parameter of domain test_name is not valid",
                     self.domain_conf._ConfigurationDomain__parse_cpu,
                     invalid_config)

class TestConfigurationDomainMemory(CloubedTestCase):

    def setUp(self):
        self._domain_item = valid_domain_item
        self.domain_conf = ConfigurationDomain(self._domain_item)

    def test_parse_memory_ok(self):
        """
            ConfigurationDomain.__parse_memory() should convert valid memory in
            parameter into an integer representing the number of MB
        """
        valid_memories = { '1GB'   : 1024,
                           2       : 2048,
                           '512M'  : 512,
                           '512MB' : 512,
                           '512MiB': 512,
                           '512 M' : 512 }
        for memory, expected_value in valid_memories.iteritems():
            config = { 'memory': memory }
            self.domain_conf._ConfigurationDomain__parse_memory(config)
            self.assertEqual(self.domain_conf.get_memory(),
                             expected_value)

    def test_parse_memory_missing(self):
        """
            ConfigurationDomain.__parse_memory() should raise
            CloubedConfigurationException when the memory parameter is missing
        """

        invalid_config = { }
        self.assertRaisesRegexp(
                 CloubedConfigurationException,
                 "memory parameter of domain test_name is missing",
                 self.domain_conf._ConfigurationDomain__parse_memory,
                 invalid_config)

    def test_parse_memory_invalid_format(self):
        """
            ConfigurationDomain.__parse_memory() should raise
            CloubedConfigurationException when the format of the memory given 
            in parameter is not valid
        """
        invalid_configs = [ { 'memory': {}    },
                            { 'memory': None  } ]

        for invalid_config in invalid_configs:
            self.assertRaisesRegexp(
                     CloubedConfigurationException,
                     "format of memory parameter of domain test_name is not " \
                     "valid",
                     self.domain_conf._ConfigurationDomain__parse_memory,
                     invalid_config)

    def test_parse_memory_invalid_str(self):
        """
            ConfigurationDomain.__parse_memory() should raise
            CloubedConfigurationException when the format of the memory string
            given in parameter is not valid
        """
        invalid_configs = [ { 'memory': 'b32' }, 
                            { 'memory': 'x'   } ]

        for invalid_config in invalid_configs:
            self.assertRaisesRegexp(
                     CloubedConfigurationException,
                     "memory size '.*' of domain test_name is not valid",
                     self.domain_conf._ConfigurationDomain__parse_memory,
                     invalid_config)


    def test_parse_memory_invalid_unit(self):
        """
            ConfigurationDomain.__parse_memory() should raise
            CloubedConfigurationException when the unit in the memory string
            given in parameter is not valid
        """

        invalid_configs = [ { 'memory': '1TB' },
                            { 'memory': '1K'  },
                            { 'memory': '1m'  },
                            { 'memory': '1Mo' } ]

        for invalid_config in invalid_configs:
            self.assertRaisesRegexp(
                     CloubedConfigurationException,
                     "unknown unit for memory '.*' of domain test_name",
                     self.domain_conf._ConfigurationDomain__parse_memory,
                     invalid_config)

class TestConfigurationDomainGraphics(CloubedTestCase):

    def setUp(self):
        self._domain_item = valid_domain_item
        self.domain_conf = ConfigurationDomain(self._domain_item)

    def test_parse_graphics_ok(self):
        """
            ConfigurationDomain.__parse_graphics() should raise
            CloubedConfigurationException when invalid graphics format is given
            in parameter
        """

        conf = { 'graphics': 'vnc' }
        self.domain_conf._ConfigurationDomain__parse_graphics(conf)
        self.assertEqual(self.domain_conf.get_graphics(), 'vnc')

    def test_parse_graphics_invalid_format(self):
        """
            ConfigurationDomain.__parse_graphics() should raise
            CloubedConfigurationException when invalid graphics format is given
            in parameter
        """

        invalid_graphics = [ { 'graphics': 4    },
                             { 'graphics': {}   },
                             { 'graphics': []   },
                             { 'graphics': None } ]

        for graphics in invalid_graphics:
            self.assertRaisesRegexp(
                     CloubedConfigurationException,
                     "format of graphics parameter of domain test_name is not " \
                     "valid",
                     self.domain_conf._ConfigurationDomain__parse_graphics,
                     graphics)

    def test_parse_graphics_invalid_value(self):
        """
            ConfigurationDomain.__parse_graphics() should raise
            CloubedConfigurationException when invalid graphics choice is given
            in parameter
        """

        invalid_graphics = { 'graphics': 'nonexisting_graphics' }

        self.assertRaisesRegexp(
                 CloubedConfigurationException,
                 "value nonexisting_graphics of graphics parameter of domain " \
                 "test_name is not valid",
                 self.domain_conf._ConfigurationDomain__parse_graphics,
                 invalid_graphics)

class TestConfigurationDomainNetifs(CloubedTestCase):

    def setUp(self):
        self._domain_item = valid_domain_item
        self.domain_conf = ConfigurationDomain(self._domain_item)

    def test_parse_netifs_missing(self):
        """
            ConfigurationDomain.__parse_netifs() should raise
            CloubedConfigurationException when the netifs section is missing
        """

        invalid_config = { }
        self.assertRaisesRegexp(
                 CloubedConfigurationException,
                 "netifs section of domain test_name is missing",
                 self.domain_conf._ConfigurationDomain__parse_netifs,
                 invalid_config)

    def test_parse_netifs_invalid_format(self):
        """
            ConfigurationDomain.__parse_netifs() should raise
            CloubedConfigurationException when invalid netifs format is given
            in parameter
        """

        invalid_configs = [ { 'netifs': 'invalid_netif' },
                            { 'netifs': {}              },
                            { 'netifs': 42              },
                            { 'netifs': None            } ]

        for invalid_config in invalid_configs:

            self.assertRaisesRegexp(
                     CloubedConfigurationException,
                     "format of netifs section of domain test_name is not "\
                     "valid",
                     self.domain_conf._ConfigurationDomain__parse_netifs,
                     invalid_config)

    def test_parse_netifs_invalid_format_2(self):
        """
            ConfigurationDomain.__parse_netifs() should raise
            CloubedConfigurationException when invalid netifs format is given
            in parameter
        """

        invalid_configs = [ { 'netifs': [ 'invalid_netif' ] },
                            { 'netifs': [ None            ] },
                            { 'netifs': [ 0, 42           ] } ]

        for invalid_config in invalid_configs:

            self.assertRaisesRegexp(
                     CloubedConfigurationException,
                     "format of netif 0 of domain test_name is not valid",
                     self.domain_conf._ConfigurationDomain__parse_netifs,
                     invalid_config)

    def test_parse_netifs_missing_network(self):
        """
            ConfigurationDomain.__parse_netifs() should raise
            CloubedConfigurationException when netifs in parameter have not any
            network name
        """

        invalid_configs = [ { 'netifs': [ {                } ] },
                            { 'netifs': [ { 'epic': 'fail' } ] } ]

        for invalid_config in invalid_configs:

            self.assertRaisesRegexp(
                     CloubedConfigurationException,
                     "network of netif 0 of domain test_name is missing",
                     self.domain_conf._ConfigurationDomain__parse_netifs,
                     invalid_config)

    def test_parse_netifs_invalid_network(self):
        """
            ConfigurationDomain.__parse_netifs() should raise
            CloubedConfigurationException when netifs in parameter have invalid
            network name
        """

        invalid_configs = [ { 'netifs': [ { 'network': None } ] },
                            { 'netifs': [ { 'network': 42   } ] } ]

        for invalid_config in invalid_configs:

            self.assertRaisesRegexp(
                     CloubedConfigurationException,
                     "format of network of netif 0 of domain test_name is " \
                     "not valid",
                     self.domain_conf._ConfigurationDomain__parse_netifs,
                     invalid_config)

    def test_parse_netifs_invalid_ip(self):
        """
            ConfigurationDomain.__parse_netifs() should raise
            CloubedConfigurationException when netifs in parameter have invalid
            IP address
        """

        invalid_configs = [ { 'netifs': [ { 'network': 'test', 'ip': None } ] },
                            { 'netifs': [ { 'network': 'test', 'ip': 42   } ] } ]

        for invalid_config in invalid_configs:

            self.assertRaisesRegexp(
                     CloubedConfigurationException,
                     "format of ip of netif 0 of domain test_name is not " \
                     "valid",
                     self.domain_conf._ConfigurationDomain__parse_netifs,
                     invalid_config)

class TestConfigurationDomainDisks(CloubedTestCase):

    def setUp(self):
        self._domain_item = valid_domain_item
        self.domain_conf = ConfigurationDomain(self._domain_item)

    def test_parse_disks_missing(self):
        """
            ConfigurationDomain.__parse_disks() should raise
            CloubedConfigurationException when the disks section is missing
        """

        invalid_config = { }
        self.assertRaisesRegexp(
                 CloubedConfigurationException,
                 "disks section of domain test_name is missing",
                 self.domain_conf._ConfigurationDomain__parse_disks,
                 invalid_config)

    def test_parse_disks_invalid_format(self):
        """
            ConfigurationDomain.__parse_disks() should raise
            CloubedConfigurationException when invalid disks format is given
            in parameter
        """

        invalid_configs = [ { 'disks': 'invalid_disk' },
                            { 'disks': {}             },
                            { 'disks': 42             },
                            { 'disks': None           } ]

        for invalid_config in invalid_configs:

            self.assertRaisesRegexp(
                     CloubedConfigurationException,
                     "format of disks section of domain test_name is not valid",
                     self.domain_conf._ConfigurationDomain__parse_disks,
                     invalid_config)

    def test_parse_disks_invalid_format_2(self):
        """
            ConfigurationDomain.__parse_disks() should raise
            CloubedConfigurationException when invalid disks format is given
            in parameter
        """

        invalid_configs = [ { 'disks': [ 'invalid_disk' ] },
                            { 'disks': [ None           ] },
                            { 'disks': [ 0, 42          ] } ]

        for invalid_config in invalid_configs:

            self.assertRaisesRegexp(
                     CloubedConfigurationException,
                     "format of disk 0 of domain test_name is not valid",
                     self.domain_conf._ConfigurationDomain__parse_disks,
                     invalid_config)

    def test_parse_disks_missing_device(self):
        """
            ConfigurationDomain.__parse_disks() should raise
            CloubedConfigurationException when disks in parameter have not any
            device
        """

        invalid_configs = [ { 'disks': [ {                                          } ] },
                            { 'disks': [ { 'epic' : 'fail'                          } ] },
                            { 'disks': [ { 'storage_volume' : 'test_storage_volume' } ] } ]

        for invalid_config in invalid_configs:

            self.assertRaisesRegexp(
                     CloubedConfigurationException,
                     "device of disk 0 of domain test_name is missing",
                     self.domain_conf._ConfigurationDomain__parse_disks,
                     invalid_config)

    def test_parse_disks_missing_storage_volume(self):
        """
            ConfigurationDomain.__parse_disks() should raise
            CloubedConfigurationException when disks in parameter have not any
            storage volume
        """

        invalid_configs = [ { 'disks': [ { 'device': 'test_device' } ] } ]

        for invalid_config in invalid_configs:

            self.assertRaisesRegexp(
                     CloubedConfigurationException,
                     "storage volume of disk 0 of domain test_name is missing",
                     self.domain_conf._ConfigurationDomain__parse_disks,
                     invalid_config)

    def test_parse_disks_invalid_device(self):
        """
            ConfigurationDomain.__parse_disks() should raise
            CloubedConfigurationException when disks in parameter have invalid
            device
        """

        invalid_configs = [ { 'disks': [ { 'device': None,
                                           'storage_volume': 'test_storage_volume' } ] },
                            { 'disks': [ { 'device' : 42,
                                           'storage_volume': 'test_storage_volume' } ] } ]

        for invalid_config in invalid_configs:

            self.assertRaisesRegexp(
                     CloubedConfigurationException,
                     "format of device of disk 0 of domain test_name is not " \
                     "valid",
                     self.domain_conf._ConfigurationDomain__parse_disks,
                     invalid_config)

    def test_parse_disks_invalid_storage_volume(self):
        """
            ConfigurationDomain.__parse_disks() should raise
            CloubedConfigurationException when disks in parameter have invalid
            storage volume
        """

        invalid_configs = [ { 'disks': [ { 'device': 'test_device',
                                           'storage_volume': None } ] },
                            { 'disks': [ { 'device': 'test_device',
                                           'storage_volume': 42 } ] } ]

        for invalid_config in invalid_configs:

            self.assertRaisesRegexp(
                     CloubedConfigurationException,
                     "format of storage volume of disk 0 of domain test_name " \
                     "is not valid",
                     self.domain_conf._ConfigurationDomain__parse_disks,
                     invalid_config)

class TestConfigurationDomainTemplates(CloubedTestCase):

    def setUp(self):
        self._domain_item = valid_domain_item
        self.domain_conf = ConfigurationDomain(self._domain_item)

    def test_parse_templates_ok(self):
        """
            ConfigurationDomain.__parse_templates() should parse valid values 
            without errors and set appropriate instance attributes
        """

        conf = { 'templates':
                     { 'files': [ { 'name': 'test_template_file_name',
                                    'input': 'test_template_file_input',
                                    'output': 'test_template_file_output' } ],
                       'vars': { 'var_name': 'var_value' } } }
        self.domain_conf._ConfigurationDomain__parse_templates(conf)
        self.assertEquals(len(self.domain_conf.get_templates_list()), 1)
        self.assertDictContainsSubset(
                          {'domain.test_name.name': 'test_name'},
                          self.domain_conf.get_absolute_templates_dict())
        self.assertDictContainsSubset(
                          {'self.name': 'test_name'},
                          self.domain_conf.get_contextual_templates_dict())

        conf = { 'templates': {} }
        self.domain_conf._ConfigurationDomain__parse_templates(conf)
        self.assertEqual(self.domain_conf.get_templates_list(), [])
        self.assertEqual(self.domain_conf._template_files, [])
        self.assertEqual(self.domain_conf._template_vars, {})

    def test_parse_templates_invalid_files_format(self):
        """
            ConfigurationDomain.__parse_templates() should raise
            CloubedConfigurationException if the format of the files section is
            not valid
        """

        invalid_conf = { 'templates': { 'files': 42  } }
        self.assertRaisesRegexp(
                 CloubedConfigurationException,
                 "format of the files sub-section in the templates section " \
                 "of domain test_name templates is not valid",
                 self.domain_conf._ConfigurationDomain__parse_templates,
                 invalid_conf)

    def test_parse_templates_files_missing_attribute(self):
        """
            ConfigurationDomain.__parse_templates() should raise
            CloubedConfigurationException if one required attribute of a
            template file is missing
        """

        invalid_conf = { 'templates':
                             { 'files': [ { 'name': 'test_template_file_name',
                                            'output': 'test_template_file_output' } ] } }
        self.assertRaisesRegexp(
                 CloubedConfigurationException,
                 "input parameter of a template file of domain test_name " \
                 "is missing",
                 self.domain_conf._ConfigurationDomain__parse_templates,
                 invalid_conf)

    def test_parse_templates_files_attribute_invalid_format(self):
        """
            ConfigurationDomain.__parse_templates() should raise
            CloubedConfigurationException if the format of one attribute of a
            template file is invalid
        """

        invalid_conf = { 'templates':
                             { 'files': [ { 'name': 'test_template_file_name',
                                            'input': 42,
                                            'output': 'test_template_file_output' } ] } }
        self.assertRaisesRegexp(
                 CloubedConfigurationException,
                 "format of input parameter of a template file of domain " \
                 "test_name is not valid",
                 self.domain_conf._ConfigurationDomain__parse_templates,
                 invalid_conf)

    def test_parse_templates_invalid_vars_format(self):
        """
            ConfigurationDomain.__parse_templates() should raise
            CloubedConfigurationException if the format of the vars section is
            not valid
        """

        invalid_conf = { 'templates':
                             { 'vars': 42 } }

        self.assertRaisesRegexp(
                 CloubedConfigurationException,
                 "format of the vars sub-section in the templates section of " \
                 "domain test_name templates is not valid",
                 self.domain_conf._ConfigurationDomain__parse_templates,
                 invalid_conf)

    def test_parse_templates_vars_attribute_invalid_format(self):
        """
            ConfigurationDomain.__parse_templates() should raise
            CloubedConfigurationException if the format of one attribute of a
            template file is invalid
        """

        invalid_conf = { 'templates':
                             { 'vars': { 'test_var_name': [] } } }

        self.assertRaisesRegexp(
                 CloubedConfigurationException,
                 "format of the value of test_var_name template variable of " \
                 "domain test_name is not valid",
                 self.domain_conf._ConfigurationDomain__parse_templates,
                 invalid_conf)

loadtestcase(TestConfigurationDomain)
loadtestcase(TestConfigurationDomainCpu)
loadtestcase(TestConfigurationDomainMemory)
loadtestcase(TestConfigurationDomainGraphics)
loadtestcase(TestConfigurationDomainNetifs)
loadtestcase(TestConfigurationDomainDisks)
loadtestcase(TestConfigurationDomainTemplates)
