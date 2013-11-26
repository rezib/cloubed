#!/usr/bin/env python

import os

from CloubedTests import *

from lib.conf.ConfigurationStoragePool import ConfigurationStoragePool
from lib.CloubedException import CloubedConfigurationException

class TestConfigurationStoragePoolPath(CloubedTestCase):

    def setUp(self):
        storage_pool_item = { 'name': 'test_name',
                              'testbed': 'test_testbed',
                              'path': 'test_path' }
        self.storage_pool_conf = ConfigurationStoragePool(storage_pool_item)

    def test_parse_path_ok(self):
        """
            ConfigurationStoragePool.__parse_path() should parse valid values
            without errors and set _path instance attribute properly
        """
        conf = { 'path': '/test_absolute_path' }
        self.storage_pool_conf._ConfigurationStoragePool__parse_path(conf)
        self.assertEqual(self.storage_pool_conf.get_path(),
                         '/test_absolute_path')

        conf = { 'path': 'test_relative_path' }
        self.storage_pool_conf._ConfigurationStoragePool__parse_path(conf)
        self.assertEqual(self.storage_pool_conf.get_path(),
                         os.path.join(os.getcwd(), 'test_relative_path') )

    def test_parse_path_missing(self):
        """
            ConfigurationStoragePool.__parse_path() should raise a
            CloubedConfigurationException if the path parameter in the
            configuration is missing
        """

        invalid_conf = { }
        self.assertRaisesRegexp(
                 CloubedConfigurationException,
                 "path parameter is missing on storage pool {name}" \
                     .format(name=self.storage_pool_conf.get_name()),
                 self.storage_pool_conf._ConfigurationStoragePool__parse_path,
                 invalid_conf)

    def test_parse_path_invalid(self):
        """
            ConfigurationStoragePool.__parse_path() should raise a
            CloubedConfigurationException if the format of path parameter in
            the configuration is not valid
        """

        invalid_confs = [ { 'path': 42   },
                          { 'path': []   },
                          { 'path': None } ]
        for invalid_conf in invalid_confs:
            self.assertRaisesRegexp(
                     CloubedConfigurationException,
                     "format of the path parameter on storage pool {name} is " \
                     "not valid" \
                         .format(name=self.storage_pool_conf.get_name()),
                     self.storage_pool_conf._ConfigurationStoragePool__parse_path,
                     invalid_conf)

class TestConfigurationStoragePoolTemplates(CloubedTestCase):

    def setUp(self):
        storage_pool_item = { 'name': 'test_name',
                              'testbed': 'test_testbed',
                              'path': '/test_path' }
        self.storage_pool_conf = ConfigurationStoragePool(storage_pool_item)

    def test_get_templates_dict(self):
        """
            ConfigurationStoragePool.get_templates_dict() should return a dict
            without all parameters of the storage pool
        """
        self.assertEqual(self.storage_pool_conf.get_templates_dict(),
                         {'storagepool.test_name.path': '/test_path'})

loadtestcase(TestConfigurationStoragePoolPath)
loadtestcase(TestConfigurationStoragePoolTemplates)
