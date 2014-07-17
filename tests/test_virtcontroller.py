#!/usr/bin/env python

import mock
from CloubedTests import *
from lib.VirtController import VirtController
from lib.StoragePool import StoragePool
from lib.conf.ConfigurationStoragePool import ConfigurationStoragePool
from lib.CloubedException import CloubedControllerException
from Mock import MockLibvirt, MockLibvirtConnect, MockLibvirtStoragePool, MockLibvirtNetwork, MockLibvirtDomain

class FakeCloubed():
    """Fake class to avoid usage of full Cloubed class in these tests"""

    def __init__(self, ctl):

        self.ctl = ctl

libvirt_mod_m = mock.Mock()
libvirt_mod_m.open.side_effect = MockLibvirt.open
libvirt_mod_m.openReadOnly.side_effect = MockLibvirt.openReadOnly

libvirt_conn_m = mock.Mock()
libvirt_conn_m.return_value = MockLibvirtConnect

class TestVirtController(CloubedTestCase):

    def setUp(self):

        patcher_open = mock.patch('libvirt.open', libvirt_mod_m.open)
        patcher_openro = mock.patch('libvirt.openReadOnly', libvirt_mod_m.openReadOnly)
        patcher_open.start()
        patcher_openro.start()
        self.addCleanup(patcher_open.stop)
        self.addCleanup(patcher_openro.stop)

    def test_new_virt_controller(self):
        """Checks that VirtController.__init__() correctly calls proper
           functions in Libvirt
        """
        ctl = VirtController()
        ctl = VirtController(read_only=True)
        self.assertIsNot(ctl.conn, None)
        libvirt_mod_m.open.assert_called_with('qemu:///system')
        libvirt_mod_m.openReadOnly.assert_called_with('qemu:///system')

class TestVirtControllerMethods(CloubedTestCase):

    def setUp(self):

        patcher_open = mock.patch('libvirt.open', libvirt_mod_m.open)
        patcher_conn = mock.patch('libvirt.virConnect', libvirt_conn_m)
        patcher_open.start()
        patcher_conn.start()
        self.addCleanup(patcher_open.stop)
        self.addCleanup(patcher_conn.stop)
        self.ctl = VirtController()
        self.tbd = FakeCloubed(self.ctl)

    def test_find_storage_pool(self):
        """Checks that VirtController.find_storage_pool() finds the storage pool
           if existing else None
        """

        # self.ctl.conn is a MockLibvirtConnect
        self.ctl.conn.pools = []
        self.ctl.conn.defined_pools = []
        self.assertIs(self.ctl.find_storage_pool('fail'), None)

        self.ctl.conn.pools = [ MockLibvirtStoragePool('test1'), ]
        self.ctl.conn.defined_pools = [ MockLibvirtStoragePool('test2'), ]
        self.assertIsNot(self.ctl.find_storage_pool('test2'), None)

    def test_create_storage_pool(self):
        """Checks that VirtController.create_storage_pool() does not raise any
           issue
        """

        xml = "<pool type='dir'><name>pool_name</name>" \
              "<target><path>/test_pool_path</path></target></pool>"
        self.ctl.create_storage_pool(xml)

    def test_find_storage_volume(self):
        """Checks that VirtController.find_storage_volume() finds the storage
           volume in the storage pool if existing else None
        """

        pool_item = { 'name': 'test_name',
                      'testbed': 'test_testbed',
                      'path': '/test_path' }
        pool_conf = ConfigurationStoragePool(pool_item)
        storage_pool = StoragePool(self.tbd, pool_conf)

        self.assertIs(self.ctl.find_storage_volume(storage_pool,'fail'), None)

        pool = MockLibvirtStoragePool('/test_path')
        pool.volumes.append('volume1')
        self.ctl.conn.pools = [ pool, ]
        self.assertEquals(self.ctl.find_storage_volume(storage_pool,'volume1'), 'volume1')

    def test_create_storage_volume(self):
        """Checks that VirtController.create_storage_volume() does not raise
           any issue unless the storage pool does not exist and
           CloubedControllerException is raised
        """

        pool_item = { 'name': 'test_name',
                      'testbed': 'test_testbed',
                      'path': '/test_path' }
        pool_conf = ConfigurationStoragePool(pool_item)
        pool1 = StoragePool(self.tbd, pool_conf)

        xml = object()

        pool = MockLibvirtStoragePool('/test_path')
        self.ctl.conn.pools = [ pool, ]
        self.ctl.create_storage_volume(pool1, xml)

        pool_item = { 'name': 'test_name',
                      'testbed': 'test_testbed',
                      'path': '/test_path2' }
        pool_conf = ConfigurationStoragePool(pool_item)
        pool2 = StoragePool(self.tbd, pool_conf)

        self.assertRaisesRegexp(CloubedControllerException,
                                "pool /test_path2 not found by virtualization controller",
                                self.ctl.create_storage_volume,
                                pool2,
                                'volume1')

    def test_find_network(self):
        """Checks that VirtController.find_network() finds the network if
           existing else None
        """

        self.ctl.conn.networks = []
        self.ctl.conn.defined_networks = []
        self.assertIs(self.ctl.find_network('fail'), None)

        self.ctl.conn.networks = [ MockLibvirtNetwork('net1'), ]
        self.ctl.conn.defined_networks = [ MockLibvirtNetwork('net2'), ]
        self.assertIsNot(self.ctl.find_network('net1'), None)
        self.assertIsNot(self.ctl.find_network('net2'), None)

    def test_create_network(self):
        """Checks that VirtController.create_network() does not raise any
           issue
        """

        xml = "<network><name>network_name</name></network>"
        self.ctl.create_network(xml)

    def test_find_domain(self):
        """Checks that VirtController.find_domain() finds the domain if existing
           else None
        """

        self.ctl.conn.domains = []
        self.ctl.conn.defined_domains = []
        self.assertIs(self.ctl.find_domain('fail'), None)

        self.ctl.conn.domains = [ MockLibvirtDomain(0, 'domain1'), ]
        self.ctl.conn.defined_domains = [ MockLibvirtDomain(1, 'domain2'), ]
        self.assertIsNot(self.ctl.find_domain('domain1'), None)
        self.assertIsNot(self.ctl.find_domain('domain2'), None)
        self.assertIs(self.ctl.find_domain('domain3'), None)

    def test_create_domain(self):
        """Checks that VirtController.create_domain() does not raise any
           issue
        """

        xml = "<domain><name>domain_name</name></domain>"
        self.ctl.create_domain(xml)

    def test_setKeepAlive(self):
        """Checks that VirtController.setKeepAlive() does not raise any issue"""

        self.ctl.setKeepAlive(0, 1)

    def test_domain_event_register(self):
        """Checks that VirtController.domain_event_register() does not raise any
           issue
        """

        def handler():
            pass
        self.ctl.domain_event_register(handler)

class TestVirtControllerStaticMethods(CloubedTestCase):

    def test_event_register(self):
        """Checks that VirtController.event_register() properly calls
           virEventRegisterDefaultImpl() function of Libvirt
        """

        with mock.patch('libvirt.virEventRegisterDefaultImpl',) as m:
            VirtController.event_register()
            m.assert_called_once_with()

    def test_event_register(self):
        """Checks that VirtController.event_register() properly calls
           virEventRunDefaultImpl() function of Libvirt
        """

        with mock.patch('libvirt.virEventRunDefaultImpl',) as m:
            VirtController.event_run()
            m.assert_called_once_with()

    @mock.patch('libvirt.getVersion', MockLibvirt.getVersion)
    def test_support_spice(self):
        """Checks that VirtController.supports_spice() returns True if the
           version of Libvirt is >= 8.0.6
        """
        MockLibvirt.version = 8005
        self.assertIs(VirtController.supports_spice(), False)
        MockLibvirt.version = 8006
        self.assertIs(VirtController.supports_spice(), True)

loadtestcase(TestVirtController)
loadtestcase(TestVirtControllerMethods)
loadtestcase(TestVirtControllerStaticMethods)
