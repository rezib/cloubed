#!/usr/bin/env python

import copy

from CloubedTests import *
from Mock import MockConfigurationLoader

from lib.conf.Configuration import Configuration
from lib.conf.ConfigurationStoragePool import ConfigurationStoragePool
from lib.conf.ConfigurationStorageVolume import ConfigurationStorageVolume
from lib.conf.ConfigurationNetwork import ConfigurationNetwork
from lib.conf.ConfigurationDomain import ConfigurationDomain
from lib.CloubedException import CloubedConfigurationException

conf = {'testbed': 'test_testbed',
        'storagepools':
            [ { 'name': 'test_storage_pool',
                'path': 'test_path '} ],
        'storagevolumes':
            [ { 'name': 'test_storage_volume',
                'storagepool': 'test_storage_pool',
                'size': 10,
                'format': 'qcow2' } ],
        'networks':
            [ { 'name': 'test_network' } ],
        'domains':
            [ { 'name': 'test_domain',
                'cpu' : 1,
                'memory': 1,
                'netifs': [],
                'disks': [] } ], }

class TestConfiguration(CloubedTestCase):

    def setUp(self):
        self._loader = MockConfigurationLoader(conf)
        self._configuration = Configuration(self._loader)

    def test_attr_storage_pools(self):
        """
            Configuration.storage_pools should be the list of parsed storage
            pools
        """
        self.assertIsInstance(self._configuration.storage_pools.pop(),
                              ConfigurationStoragePool)

    def test_attr_storage_volumes(self):
        """
            Configuration.storage_volumes should return the list of parsed
            storage volumes
        """
        self.assertIsInstance(self._configuration.storage_volumes.pop(),
                              ConfigurationStorageVolume)

    def test_attr_networks(self):
        """
            Configuration.networks should be the list of parsed
            networks
        """
        self.assertIsInstance(self._configuration.networks.pop(),
                              ConfigurationNetwork)

    def test_attr_domains(self):
        """
            Configuration.domains should return the list of parsed domains
        """
        self.assertIsInstance(self._configuration.domains.pop(),
                              ConfigurationDomain)

    def test_get_templates_dict(self):
        """
            Configuration.get_templates_dict() should return a dict with all
            parameters of the configuration
        """
        self.assertDictContainsSubset(
                 {'testbed': 'test_testbed'},
                 self._configuration.get_templates_dict('test_domain'))

class TestConfigurationTestbed(CloubedTestCase):
 
    def setUp(self):
        self._loader = MockConfigurationLoader(conf)
        self._configuration = Configuration(self._loader)

    def test_parse_testbed_ok(self):
        """
            Configuration.__parse_testbed should properly set the testbed
            parameter if the given input is correct 
        """
        conf = { 'testbed': 'new_test_testbed' }

        self._configuration._Configuration__parse_testbed(conf)
        self.assertEqual(self._configuration.testbed, 'new_test_testbed')

    def test_parse_testbed_missing(self):
        """
            Configuration.__parse_testbed should raise
            CloubedConfigurationException if the testbed parameter is missing
        """
        invalid_conf = { }

        self.assertRaisesRegexp(CloubedConfigurationException,
                                "testbed parameter is missing",
                                self._configuration._Configuration__parse_testbed,
                                invalid_conf)

    def test_parse_testbed_invalid(self):
        """
            Configuration.__parse_testbed should raise
            CloubedConfigurationException if the format of the testbed parameter
            is invalid
        """
        invalid_confs = [ { 'testbed': 42   },
                          { 'testbed': []   },
                          { 'testbed': None } ]

        for invalid_conf in invalid_confs:
            self.assertRaisesRegexp(CloubedConfigurationException,
                                    "format of the testbed parameter is not valid",
                                    self._configuration._Configuration__parse_testbed,
                                    invalid_conf)

class TestConfigurationItems(CloubedTestCase):

    def setUp(self):
        self._loader = MockConfigurationLoader(conf)
        self._configuration = Configuration(self._loader)

    def test_parse_items_ok(self):
        """
            Configuration.__parse_items() should properly set the list of items
            if the given input is correct 
        """
        conf = { 'storagepools': [
                     { 'name': 'test_storage_pool',
                       'path': 'test_path' } ],
                 'storagevolumes': [ ],
                 'networks': [ ],
                 'domains': [ ] }
        
        self._configuration._Configuration__parse_items(conf)
        self.assertIsInstance(self._configuration.storage_pools.pop(),
                              ConfigurationStoragePool)

    def test_parse_items_missing_section(self):
        """
            Configuration.__parse_items() should raise
            CloubedConfigurationException if one of the main items section is
            missing
        """
        invalid_conf = { 'storagevolumes': [ ],
                         'networks': [ ],
                         'domains': [ ] }
        
        self.assertRaisesRegexp(CloubedConfigurationException,
                                "storagepools parameter is missing",
                                self._configuration._Configuration__parse_items,
                                invalid_conf)

    def test_parse_items_invalid_format(self):
        """
            Configuration.__parse_items() should raise
            CloubedConfigurationException if the format of one of the main items
            sections is not valid
        """
        invalid_conf = { 'storagepools': [ ],
                         'storagevolumes': [ ],
                         'networks': 'fail',
                         'domains': [ ] }
        
        self.assertRaisesRegexp(CloubedConfigurationException,
                                "format of networks parameter is not valid",
                                self._configuration._Configuration__parse_items,
                                invalid_conf)

class TestConfigurationTemplates(CloubedTestCase):

    def setUp(self):
        self._loader = MockConfigurationLoader(conf)
        self._configuration = Configuration(self._loader)

    def test_parse_templates_ok(self):
        """
            Configuration.__parse_templates() should properly set the list of items
            if the given input is correct 
        """
        conf = { 'templates': { 'test_var': 'test_val' } }
        self._configuration._Configuration__parse_templates(conf)
        self.assertEquals(self._configuration._templates,
                          { 'testbed.test_var': 'test_val' })

        conf = { 'templates': {} }
        self._configuration._Configuration__parse_templates(conf)
        self.assertEquals(self._configuration._templates, {})

        conf = { }
        self._configuration._Configuration__parse_templates(conf)
        self.assertEquals(self._configuration._templates, {})

    def test_parse_templates_invalid_format(self):
        """
            Configuration.__parse_templates() should raise
            CloubedConfigurationException if the format of templates section is
            not valid
        """
        invalid_confs = [ { 'templates': None },
                          { 'templates': [] },
                          { 'templates': 'fail' } ]
                         
        for invalid_conf in invalid_confs:
            self.assertRaisesRegexp(CloubedConfigurationException,
                                    "format of the templates section is not valid",
                                    self._configuration._Configuration__parse_templates,
                                    invalid_conf)

    def test_parse_templates_invalid_variable(self):
        """
            Configuration.__parse_templates() should raise
            CloubedConfigurationException if the format of templates section is
            not valid
        """
        invalid_confs = [ { 'templates': { 'test': None } },
                          { 'templates': { 'test': []   } },
                          { 'templates': { 'test': 42   } } ]
                         
        for invalid_conf in invalid_confs:
            self.assertRaisesRegexp(CloubedConfigurationException,
                                    "format of the value of the global template " \
                                    "variable test is not valid",
                                    self._configuration._Configuration__parse_templates,
                                    invalid_conf)


loadtestcase(TestConfiguration)
loadtestcase(TestConfigurationTestbed)
loadtestcase(TestConfigurationItems)
loadtestcase(TestConfigurationTemplates)
