#!/usr/bin/python3

import os

from CloubedTests import *

from cloubed.conf.Configuration import Configuration
from cloubed.conf.ConfigurationItem import ConfigurationItem
from cloubed.conf.ConfigurationStoragePool import ConfigurationStoragePool
from cloubed.CloubedException import CloubedConfigurationException
from Mock import MockConfigurationLoader, conf_minimal

class TestConfigurationItem(CloubedTestCase):

    def setUp(self):
        self._loader = MockConfigurationLoader(conf_minimal)
        self.conf = Configuration(self._loader)
        item = { 'name': 'test_name' }
        self.item_conf = ConfigurationItem(self.conf, item)

    def test_attr_name(self):
        """
            ConfigurationItem.name should be the name of the
            item
        """
        self.assertEqual(self.item_conf.name,
                         "test_name")

    def test_attr_testbed(self):
        """
            ConfigurationItem.testbed should be the name of the
            testbed
        """
        self.assertEqual(self.item_conf.testbed,
                         "test_testbed")

    def test_get_type(self):
        """
            ConfigurationItem._get_type() should raise NotImplementedError
            exception since it is an abstract class
        """
        self.assertRaises(NotImplementedError,
                          self.item_conf._get_type)

class TestConfigurationItemName(CloubedTestCase):

    # Tests of abstract ConfigurationItem.__parse_name are made through
    # ConfigurationStoragePool class since it needs to use a working
    # implementation of _get_type() method

    def setUp(self):
        storage_pool_item = { 'name': 'test_name',
                              'path': 'test_path' }
        self._loader = MockConfigurationLoader(conf_minimal)
        self.conf = Configuration(self._loader)
        self.storage_pool_conf = ConfigurationStoragePool(self.conf, storage_pool_item)

    def test_parse_name_missing(self):
        """
            ConfigurationItem.__parse_name() should raise
            CloubedConfigurationException if the name parameter is missing
        """
        invalid_conf = { 'path': 'test_path' }
        
        self.assertRaisesRegex(
                 CloubedConfigurationException,
                 "one storage pool object does not have a name",
                 self.storage_pool_conf._ConfigurationItem__parse_name,
                 invalid_conf)

    def test_parse_name_invalid_format(self):
        """
            ConfigurationItem.__parse_name() should raise
            CloubedConfigurationException if the format of the name parameter
            is invalid
        """
        invalid_conf = { "name": 42,
                         "path": "test_path" }
        
        self.assertRaisesRegex(
                 CloubedConfigurationException,
                 "the format of one storage pool object is not valid",
                 self.storage_pool_conf._ConfigurationItem__parse_name,
                 invalid_conf)

loadtestcase(TestConfigurationItem)
loadtestcase(TestConfigurationItemName)
