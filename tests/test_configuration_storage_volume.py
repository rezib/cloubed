#!/usr/bin/env python

from CloubedTests import *

from cloubed.conf.Configuration import Configuration
from cloubed.conf.ConfigurationStorageVolume import ConfigurationStorageVolume
from cloubed.CloubedException import CloubedConfigurationException
from Mock import MockConfigurationLoader, conf_minimal

class TestConfigurationStorageVolume(CloubedTestCase):

    def setUp(self):
        storage_volume_item = { 'name': 'test_name',
                                'format': 'qcow2',
                                'size': 30,
                                'storagepool': 'test_storage_pool',
                                'backing': 'test_backing' }
        self._loader = MockConfigurationLoader(conf_minimal)
        self.conf = Configuration(self._loader)
        self.storage_volume_conf = \
            ConfigurationStorageVolume(self.conf, storage_volume_item)

    def test_get_type(self):
        """
            ConfigurationStorageVolume._get_type() should return storage volume
        """
        self.assertEqual(self.storage_volume_conf._get_type(), 'storage volume')


    def test_attr_format(self):
        """
            ConfigurationStorageVolume.format should be the format of the
            storage volume
        """
        self.assertEqual(self.storage_volume_conf.format,
                         'qcow2')

    def test_attr_size(self):
        """
            ConfigurationStorageVolume.size should be the size of the storage
            volume
        """
        self.assertEqual(self.storage_volume_conf.size,
                         30)

    def test_attr_storage_pool(self):
        """
            ConfigurationStorageVolume.storage_pool should be the name of the
            storage pool
        """
        self.assertEqual(self.storage_volume_conf.storage_pool,
                         'test_storage_pool')

    def test_attr_backing(self):
        """
            ConfigurationStorageVolume.backing should be the name of the
            (optional) backing storage volume
        """
        self.assertEqual(self.storage_volume_conf.backing,
                         'test_backing')

class TestConfigurationStorageVolumeSize(CloubedTestCase):

    def setUp(self):
        storage_volume_item = { 'name': 'test_name',
                                'format': 'qcow2',
                                'size': 30,
                                'storagepool': 'test_storage_pool' }
        self._loader = MockConfigurationLoader(conf_minimal)
        self.conf = Configuration(self._loader)
        self.storage_volume_conf = \
            ConfigurationStorageVolume(self.conf, storage_volume_item)

    def test_parse_size_ok(self):
        """
            ConfigurationStorageVolume.__parse_size() should parse valid
            values without error and properly set _size instance attribute
        """
        conf = { 'size': 50 }
        self.storage_volume_conf._ConfigurationStorageVolume__parse_size(conf)
        self.assertEqual(self.storage_volume_conf.size, 50)

    def test_parse_size_missing(self):
        """
            ConfigurationStorageVolume.__parse_size() should raise
            CloubedConfigurationException when size parameter is missing
        """
        invalid_conf = { }

        self.assertRaisesRegexp(
                 CloubedConfigurationException,
                 "size parameter of storage volume {name} is missing" \
                     .format(name=self.storage_volume_conf.name),
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
                         .format(name=self.storage_volume_conf.name),
                     self.storage_volume_conf._ConfigurationStorageVolume__parse_size,
                     invalid_conf)

class TestConfigurationStorageVolumeStoragePool(CloubedTestCase):

    def setUp(self):
        self.item_conf = { 'name': 'test_name',
                           'format': 'qcow2',
                           'size': 30,
                           'storagepool': 'test_storage_pool' }

    def create_item(self, conf):
        """Create Configuration object with conf dict in parameter and then
           ConfigurationStorageVolume object with self.conf_item"""
        loader = MockConfigurationLoader(conf)
        configuration = Configuration(loader)
        self.storage_volume_conf = \
            ConfigurationStorageVolume(configuration, self.item_conf)

    def test_parse_storage_pool_ok(self):
        """
            ConfigurationStorageVolume.__parse_storage_pool() should parse
            valid without error and properly set _storage_pool instance
            attribute
        """
        vol_pool_conf_ok = { 'storagepool': 'test_storage_pool_bis' }
        conf = conf_minimal
        conf['storagepools'] = [ { 'name': 'pool1',
                                   'path': 'path1' },
                                 { 'name': 'pool2',
                                   'path': 'path2' }, ]
        self.create_item(conf)
        self.storage_volume_conf._ConfigurationStorageVolume__parse_storage_pool(vol_pool_conf_ok)
        self.assertEqual(self.storage_volume_conf.storage_pool,
                         'test_storage_pool_bis')

    def test_parse_storage_pool_missing(self):
        """
            ConfigurationStorageVolume.__parse_storage_pool() should accept
            empty storagepool parameter if only one pool available or raise
            CloubedConfigurationException when several pools
        """
        vol_pool_conf_empty = { }

        conf = conf_minimal
        conf['storagepools'] = [ { 'name': 'pool1',
                                   'path': 'path1' } ]

        self.create_item(conf)
        self.storage_volume_conf._ConfigurationStorageVolume__parse_storage_pool(vol_pool_conf_empty)
        self.assertEqual(self.storage_volume_conf.storage_pool,
                         'pool1')

        del conf['storagepools']

        self.create_item(conf)
        self.storage_volume_conf._ConfigurationStorageVolume__parse_storage_pool(vol_pool_conf_empty)
        self.assertEqual(self.storage_volume_conf.storage_pool,
                         'pool')

        conf['storagepools'] = [ { 'name': 'pool1',
                                   'path': 'path1' },
                                 { 'name': 'pool2',
                                   'path': 'path2' }, ]

        self.create_item(conf)
        self.assertRaisesRegexp(
                 CloubedConfigurationException,
                 "storagepool parameter of storage volume {name} is missing" \
                     .format(name=self.storage_volume_conf.name),
                 self.storage_volume_conf._ConfigurationStorageVolume__parse_storage_pool,
                 vol_pool_conf_empty)

    def test_parse_storage_pool_invalid_format(self):
        """
            ConfigurationStorageVolume.__parse_storage_pool() should raise
            CloubedConfigurationException when the format of the storagepool
            parameter is not valid
        """
        invalid_confs = [ { 'storagepool': 42   },
                          { 'storagepool': []   },
                          { 'storagepool': None } ]

        self._loader = MockConfigurationLoader(conf_minimal)
        self.conf = Configuration(self._loader)
        self.storage_volume_conf = \
            ConfigurationStorageVolume(self.conf, self.item_conf)

        for invalid_conf in invalid_confs:
            self.assertRaisesRegexp(
                     CloubedConfigurationException,
                     "format of storagepool parameter of storage volume {name} " \
                     "is not valid" \
                         .format(name=self.storage_volume_conf.name),
                     self.storage_volume_conf._ConfigurationStorageVolume__parse_storage_pool,
                     invalid_conf)

class TestConfigurationStorageVolumeFormat(CloubedTestCase):

    def setUp(self):
        storage_volume_item = { 'name': 'test_name',
                                'format': 'qcow2',
                                'size': 30,
                                'storagepool': 'test_storage_pool' }
        self._loader = MockConfigurationLoader(conf_minimal)
        self.conf = Configuration(self._loader)
        self.storage_volume_conf = \
            ConfigurationStorageVolume(self.conf, storage_volume_item)

    def test_parse_format_ok(self):
        """
            ConfigurationStorageVolume.__parse_format() should parse
            valid without error and properly set _format instance
            attribute
        """

        conf = { 'format': 'raw' }
        self.storage_volume_conf._ConfigurationStorageVolume__parse_format(conf)
        self.assertEqual(self.storage_volume_conf.format, 'raw')

        conf = { }
        self.storage_volume_conf._ConfigurationStorageVolume__parse_format(conf)
        self.assertEqual(self.storage_volume_conf.format, 'qcow2')

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
                         .format(name=self.storage_volume_conf.name),
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
                     .format(name=self.storage_volume_conf.name),
                 self.storage_volume_conf._ConfigurationStorageVolume__parse_format,
                 invalid_conf)

class TestConfigurationStorageVolumeBacking(CloubedTestCase):

    def setUp(self):
        storage_volume_item = { 'name': 'test_name',
                                'format': 'qcow2',
                                'size': 30,
                                'storagepool': 'test_storage_pool' }
        self._loader = MockConfigurationLoader(conf_minimal)
        self.conf = Configuration(self._loader)
        self.storage_volume_conf = \
            ConfigurationStorageVolume(self.conf, storage_volume_item)

    def test_parse_backing_ok(self):
        """
            ConfigurationStorageVolume.__parse_backing() should parse valid
            backing parameter without error and properly set backing instance
            attribute
        """
        conf = { 'backing': 'test_backing' }
        self.storage_volume_conf._ConfigurationStorageVolume__parse_backing(conf)
        self.assertEqual(self.storage_volume_conf.backing,
                         'test_backing')
        # backing parameter is optional, backing attribute should be None in
        # this case
        conf = { }
        self.storage_volume_conf._ConfigurationStorageVolume__parse_backing(conf)
        self.assertEqual(self.storage_volume_conf.backing,
                         None)

    def test_parse_backing_invalid_format(self):
        """
            ConfigurationStorageVolume.__parse_backing() should raise
            CloubedConfigurationException when the format of the backing
            parameter is not valid
        """
        invalid_confs = [ { 'backing': 42   },
                          { 'backing': []   } ]

        for invalid_conf in invalid_confs:
            self.assertRaisesRegexp(
                     CloubedConfigurationException,
                     "format of backing parameter of storage volume {name} " \
                     "is not valid" \
                         .format(name=self.storage_volume_conf.name),
                     self.storage_volume_conf._ConfigurationStorageVolume__parse_backing,
                     invalid_conf)


loadtestcase(TestConfigurationStorageVolume)
loadtestcase(TestConfigurationStorageVolumeSize)
loadtestcase(TestConfigurationStorageVolumeStoragePool)
loadtestcase(TestConfigurationStorageVolumeFormat)
loadtestcase(TestConfigurationStorageVolumeBacking)
