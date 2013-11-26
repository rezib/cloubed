#!/usr/bin/env python

from CloubedTests import *

from lib.conf.ConfigurationStorageVolume import ConfigurationStorageVolume
from lib.CloubedException import CloubedConfigurationException

class TestConfigurationStorageVolume(CloubedTestCase):

    def setUp(self):
        storage_volume_item = { 'name': 'test_name',
                                'testbed': 'test_testbed',
                                'format': 'qcow2',
                                'size': 30,
                                'storagepool': 'test_storage_pool' }
        self.storage_volume_conf = \
            ConfigurationStorageVolume(storage_volume_item)

    def test_get_type(self):
        """
            ConfigurationStorageVolume._get_type() should return storage volume
        """
        self.assertEqual(self.storage_volume_conf._get_type(), 'storage volume')


    def test_get_format(self):
        """
            ConfigurationStorageVolume.get_format() should return the format of
            the storage volume
        """
        self.assertEqual(self.storage_volume_conf.get_format(),
                         'qcow2')

    def test_get_size(self):
        """
            ConfigurationStorageVolume.get_size() should return the size of the
            storage volume
        """
        self.assertEqual(self.storage_volume_conf.get_size(),
                         30)

    def test_get_storage_pool(self):
        """
            ConfigurationStorageVolume.get_storage_pool() should return the name
            of the storage pool
        """
        self.assertEqual(self.storage_volume_conf.get_storage_pool(),
                         'test_storage_pool')

class TestConfigurationStorageVolumeSize(CloubedTestCase):

    def setUp(self):
        storage_volume_item = { 'name': 'test_name',
                                'testbed': 'test_testbed',
                                'format': 'qcow2',
                                'size': 30,
                                'storagepool': 'test_storage_pool' }
        self.storage_volume_conf = \
            ConfigurationStorageVolume(storage_volume_item)

    def test_parse_size_ok(self):
        """
            ConfigurationStorageVolume.__parse_size() should parse valid
            values without error and properly set _size instance attribute
        """
        conf = { 'size': 50 }
        self.storage_volume_conf._ConfigurationStorageVolume__parse_size(conf)
        self.assertEqual(self.storage_volume_conf.get_size(), 50)

    def test_parse_size_missing(self):
        """
            ConfigurationStorageVolume.__parse_size() should raise
            CloubedConfigurationException when size parameter is missing
        """
        invalid_conf = { }

        self.assertRaisesRegexp(
                 CloubedConfigurationException,
                 "size parameter of storage volume {name} is missing" \
                     .format(name=self.storage_volume_conf.get_name()),
                 self.storage_volume_conf._ConfigurationStorageVolume__parse_size,
                 invalid_conf)

    def test_parse_size_invalid_format(self):
        """
            ConfigurationStorageVolume.__parse_size() should raise
            CloubedConfigurationException when the format of the size parameter
            is not valid
        """
        invalid_confs = [ { 'size': 'fail' },
                          { 'size': []     },
                          { 'size': None   } ]

        for invalid_conf in invalid_confs:
            self.assertRaisesRegexp(
                     CloubedConfigurationException,
                     "format of size parameter of storage volume {name} " \
                     "is not valid" \
                         .format(name=self.storage_volume_conf.get_name()),
                     self.storage_volume_conf._ConfigurationStorageVolume__parse_size,
                     invalid_conf)

class TestConfigurationStorageVolumeStoragePool(CloubedTestCase):

    def setUp(self):
        storage_volume_item = { 'name': 'test_name',
                                'testbed': 'test_testbed',
                                'format': 'qcow2',
                                'size': 30,
                                'storagepool': 'test_storage_pool' }
        self.storage_volume_conf = \
            ConfigurationStorageVolume(storage_volume_item)

    def test_parse_storage_pool_ok(self):
        """
            ConfigurationStorageVolume.__parse_storage_pool() should parse
            valid without error and properly set _storage_pool instance
            attribute
        """
        conf = { 'storagepool': 'test_storage_pool_bis' }
        self.storage_volume_conf._ConfigurationStorageVolume__parse_storage_pool(conf)
        self.assertEqual(self.storage_volume_conf.get_storage_pool(), 
                         'test_storage_pool_bis')

    def test_parse_storage_pool_missing(self):
        """
            ConfigurationStorageVolume.__parse_storage_pool() should raise
            CloubedConfigurationException when storagepool parameter is missing
        """
        invalid_conf = { }

        self.assertRaisesRegexp(
                 CloubedConfigurationException,
                 "storagepool parameter of storage volume {name} is missing" \
                     .format(name=self.storage_volume_conf.get_name()),
                 self.storage_volume_conf._ConfigurationStorageVolume__parse_storage_pool,
                 invalid_conf)

    def test_parse_storage_pool_invalid_format(self):
        """
            ConfigurationStorageVolume.__parse_storage_pool() should raise
            CloubedConfigurationException when the format of the storagepool
            parameter is not valid
        """
        invalid_confs = [ { 'storagepool': 42   },
                          { 'storagepool': []   },
                          { 'storagepool': None } ]

        for invalid_conf in invalid_confs:
            self.assertRaisesRegexp(
                     CloubedConfigurationException,
                     "format of storagepool parameter of storage volume {name} " \
                     "is not valid" \
                         .format(name=self.storage_volume_conf.get_name()),
                     self.storage_volume_conf._ConfigurationStorageVolume__parse_storage_pool,
                     invalid_conf)

class TestConfigurationStorageVolumeFormat(CloubedTestCase):

    def setUp(self):
        storage_volume_item = { 'name': 'test_name',
                                'testbed': 'test_testbed',
                                'format': 'qcow2',
                                'size': 30,
                                'storagepool': 'test_storage_pool' }
        self.storage_volume_conf = \
            ConfigurationStorageVolume(storage_volume_item)

    def test_parse_format_ok(self):
        """
            ConfigurationStorageVolume.__parse_format() should parse
            valid without error and properly set _format instance
            attribute
        """

        conf = { 'format': 'raw' }
        self.storage_volume_conf._ConfigurationStorageVolume__parse_format(conf)
        self.assertEqual(self.storage_volume_conf.get_format(), 'raw')

        conf = { }
        self.storage_volume_conf._ConfigurationStorageVolume__parse_format(conf)
        self.assertEqual(self.storage_volume_conf.get_format(), 'qcow2')

    def test_parse_format_invalid_format(self):
        """
            ConfigurationStorageVolume.__parse_format() should raise
            CloubedConfigurationException when the format of format parameter
            is not valid
        """
        invalid_confs = [ { 'format': 42   },
                          { 'format': []   },
                          { 'format': None } ]

        for invalid_conf in invalid_confs:
            self.assertRaisesRegexp(
                     CloubedConfigurationException,
                     "format of format parameter of storage volume {name} " \
                     "is not valid" \
                         .format(name=self.storage_volume_conf.get_name()),
                     self.storage_volume_conf._ConfigurationStorageVolume__parse_format,
                     invalid_conf)

    def test_parse_format_invalid_value(self):
        """
            ConfigurationStorageVolume.__parse_format() should raise
            CloubedConfigurationException when the value of the format parameter
            is not valid
        """
        invalid_conf = { 'format': 'fail' }

        self.assertRaisesRegexp(
                 CloubedConfigurationException,
                 "value of format parameter of storage volume {name} is not valid" \
                     .format(name=self.storage_volume_conf.get_name()),
                 self.storage_volume_conf._ConfigurationStorageVolume__parse_format,
                 invalid_conf)

loadtestcase(TestConfigurationStorageVolume)
loadtestcase(TestConfigurationStorageVolumeSize)
loadtestcase(TestConfigurationStorageVolumeStoragePool)
loadtestcase(TestConfigurationStorageVolumeFormat)
