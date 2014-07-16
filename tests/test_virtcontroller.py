#!/usr/bin/env python

import mock
from xml.dom.minidom import Document
from libvirt import libvirtError
from CloubedTests import *
from lib.VirtController import VirtController
from lib.StoragePool import StoragePool
from lib.conf.ConfigurationStoragePool import ConfigurationStoragePool
from lib.CloubedException import CloubedControllerException

class MockLibvirt():

    """Class with static methods to mock all used functions in libvirt module"""

    version = 8006

    def __init__(self):
        pass

    @staticmethod
    def open(hyp):
        """Mock of libvirt.open(name)"""
        return MockLibvirtConnect(hyp)
        #pass

    @staticmethod
    def openReadOnly(hyp):
        """Mock of libvirt.openReadOnly(name)"""
        return MockLibvirtConnect(hyp, read_only=True)
        #pass

    @staticmethod
    def virEventRegisterDefaultImpl():
        """Mock of libvirt.virEventRegisterDefaultImpl()"""
        pass

    @staticmethod
    def virEventRunDefaultImpl():
        """Mock of libvirt.virEventRunDefaultImpl()"""
        pass

    @staticmethod
    def getVersion():
        """Mock of libvirt.getVersion()"""
        return MockLibvirt.version

class MockLibvirtConnect():

    """Class to mock libvirt.virConnect class and its methods used in Cloubed"""

    def __init__(self, hyp, read_only=False):

        self.hyp = hyp
        self.ro = read_only

        self.pools = []
        self.defined_pools = []

        self.networks = []
        self.defined_networks = []

        self.domains = []
        self.defined_domains = []

    def listStoragePools(self):
        """Mock of libvirt.virConnect.listStoragePools()"""

        return [ pool.name for pool in self.pools ]

    def listDefinedStoragePools(self):
        """Mock of libvirt.virConnect.listDefinedStoragePools()"""

        return [ pool.name for pool in self.defined_pools ]

    def storagePoolLookupByName(self, path):
        """Mock of libvirt.virConnect.storagePoolLookupByName()"""
        try:
            return next((pool for pool in self.pools + self.defined_pools \
                              if pool.path == path))
        except StopIteration:
            raise libvirtError("Storage pool not found: no pool with matching" \
                               "name '{path}'".format(path=path))

    def storagePoolCreateXML(self, xml, flag):
        """Mock of libvirt.virConnect.storagePoolCreateXML()"""

        pass

    def listNetworks(self):
        """Mock of libvirt.virConnect.listNetworks()"""

        return [ network.name for network in self.networks ]

    def listDefinedNetworks(self):
        """Mock of libvirt.virConnect.listDefinedNetworks()"""

        return [ network.name for network in self.defined_networks ]

    def networkLookupByName(self, name):
        """Mock of libvirt.virConnect.networkLookupByName()"""

        try:
            return next((net for net in self.networks + self.defined_networks \
                             if net.name == name))
        except StopIteration:
            raise libvirtError("Network not found: no network with matching" \
                               "name '{name}'".format(name=name))

    def networkCreateXML(self, xml):
        """Mock of libvirt.virConnect.networkCreateXML()"""

        pass

    def listDomainsID(self):
        """Mock of libvirt.virConnect.listDomainsID()"""

        return [ domain.id for domain in self.domains ]

    def listDefinedDomains(self):
        """Mock of libvirt.virConnect.listDefinedDomains()"""

        return [ domain._name for domain in self.defined_domains ]

    def lookupByID(self, id):
        """Mock of libvirt.virConnect.lookupByID()"""

        try:
            return next((domain for domain \
                                in self.domains + self.defined_domains \
                                if domain.id == id))
        except StopIteration:
            raise libvirtError("Domain not found: no domain with matching" \
                               "id {id}".format(id=id))

    def lookupByName(self, name):
        """Mock of libvirt.virConnect.lookupByName()"""

        try:
            return next((domain for domain \
                                in self.domains + self.defined_domains \
                                if domain._name == name))
        except StopIteration:
            raise libvirtError("Domain not found: no domain with matching" \
                               "name '{name}'".format(name=name))

    def createXML(self, xml, flags):
        """Mock of libvirt.virConnect.createXML()"""

        pass

    def setKeepAlive(self, major, minor):
        """Mock of libvirt.virConnect.setKeepAlive()"""

        pass

    def domainEventRegisterAny(self, dom, eventID, cb, opaque):
        """Mock of libvirt.virConnect.domainEventRegisterAny()"""

        pass

class MockLibvirtStoragePool():

    """Class to mock libvirt.virStoragePool class and its methods used in
       Cloubed
    """

    def __init__(self, name):

        self.name = name
        self.path = name
        self.volumes = []

    def XMLDesc(self, flag):
        """Mock of libvirt.virStoragePool.XMLDesc()"""

        doc = Document()
        elt = doc.createElement("path")
        txt = doc.createTextNode(self.path)
        elt.appendChild(txt)
        doc.appendChild(elt)
        return doc.toxml()

    def listVolumes(self):
        """Mock of libvirt.virStoragePool.listVolumes()"""

        return self.volumes

    def storageVolLookupByName(self, name):
        """Mock of libvirt.virStoragePool.storageVolLookupByName()"""

        try:
            return next((vol for vol in self.volumes \
                             if vol == name))
        except StopIteration:
            raise libvirtError("Storage volume not found: no storage vol " \
                               "with matching name '{name}'".format(name=name))

    def createXML(self, xml, flag):
        """Mock of libvirt.virStoragePool.createXML()"""

        pass

class MockLibvirtNetwork():

    """Class to mock libvirt.virNetwork class and its methods used in
       Cloubed
    """

    def __init__(self, name):

        self.name = name

class MockLibvirtDomain():

    """Class to mock libvirt.virDomain class and its methods used in
       Cloubed
    """

    def __init__(self, id, name):

        self.id = id
        self._name = name

    def name(self):
        """Mock of libvirt.virDomain.name()"""

        return self._name

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
        self.assertIs(self.ctl.find_storage_pool('test'), None)

        self.ctl.conn.pools = [ MockLibvirtStoragePool('test1'), ]
        self.ctl.conn.defined_pools = [ MockLibvirtStoragePool('test2'), ]
        self.assertIsNot(self.ctl.find_storage_pool('test2'), None)

    def test_create_storage_pool(self):
        """Checks that VirtController.create_storage_pool() does not raise any
           issue
        """

        xml = object()
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
        self.assertIs(self.ctl.find_network('net1'), None)

        self.ctl.conn.networks = [ MockLibvirtNetwork('net1'), ]
        self.ctl.conn.defined_networks = [ MockLibvirtNetwork('net2'), ]
        self.assertIsNot(self.ctl.find_network('net1'), None)
        self.assertIsNot(self.ctl.find_network('net2'), None)

    def test_create_network(self):
        """Checks that VirtController.create_network() does not raise any
           issue
        """

        xml = object()
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

        xml = object()
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
