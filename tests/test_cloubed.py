#!/usr/bin/env python

import mock

from CloubedTests import *
from Mock import MockConfigurationLoader, MockLibvirt, MockLibvirtConnect, MockLibvirtStoragePool, MockLibvirtNetwork, MockLibvirtDomain

from cloubed.Cloubed import Cloubed
from cloubed.CloubedException import CloubedException
from cloubed.StoragePool import StoragePool
from cloubed.StorageVolume import StorageVolume
from cloubed.Network import Network
from cloubed.Domain import Domain
from cloubed.Utils import getuser

#import logging
#logging.basicConfig(format='%(levelname)-7s: %(message)s',
#                    level=logging.DEBUG)

libvirt_mod_m = mock.Mock()
libvirt_mod_m.open.side_effect = MockLibvirt.open
libvirt_mod_m.openReadOnly.side_effect = MockLibvirt.openReadOnly

libvirt_conn_m = mock.Mock()
libvirt_conn_m.return_value = MockLibvirtConnect

conf = \
  {
    'testbed': 'test_testbed',
    'storagepools':
      [ { 'name': 'test_storage_pool',
          'path': '/test_path'} ],
    'storagevolumes':
      [ { 'name': 'test_storage_volume1',
          'storagepool': 'test_storage_pool',
          'size': 10,
          'format': 'qcow2' },
        { 'name': 'test_storage_volume2',
          'storagepool': 'test_storage_pool',
          'size': 20,
          'format': 'qcow2',
          'backing': 'test_storage_volume1' } ],
    'networks':
      [ { 'name': 'test_network1' },
        { 'name': 'test_network2',
          'forward': 'nat',
          'ip_host': '10.5.0.1',
          'netmask': '255.255.255.0',
          'dhcp': { 'start': '10.5.0.100',
                    'end': '10.5.0.110' },
          'pxe': { 'tftp_dir': 'http',
                   'boot_file': 'test.ipxe' },
        },
      ],
    'domains':
      [ { 'name': 'test_domain1',
          'cpu' : 1,
          'memory': 1,
          'netifs': [
              { 'network': 'test_network1',
                'ip': '10.5.0.10' },
          ],
          'disks': [
              { 'device': 'sda',
                'storage_volume': 'test_storage_volume1' },
          ]
        },
        { 'name': 'test_domain2',
          'cpu' : 1,
          'memory': 1,
          'netifs':
            [
              { 'network': 'test_network2',
                'ip': '10.5.0.10' },
            ],
          'disks':
            [
              { 'device': 'sda',
                'storage_volume': 'test_storage_volume2' },
            ],
          'templates':
            {
              'vars':
                {
                  'var1': 'value1',
                  'var2': 'value2',
                },
              'files':
                [
                  { 'name': 'preseed',
                    'input': 'templates/preseed.cfg',
                    'output': 'http/preseed.cfg',
                  },
                  { 'name': 'ipxe',
                    'input': 'templates/debian.ipxe',
                    'output': 'http/debian.ipxe'
                  },
                ],
            },
        },
      ],
  }

class TestCloubed(CloubedTestCase):

    def setUp(self):

        patcher_open = mock.patch('libvirt.open', libvirt_mod_m.open)
        patcher_openro = mock.patch('libvirt.openReadOnly',
                                    libvirt_mod_m.openReadOnly)
        patcher_conn = mock.patch('libvirt.virConnect', libvirt_conn_m)
        patcher_open.start()
        patcher_conn.start()
        patcher_openro.start()
        self.addCleanup(patcher_open.stop)
        self.addCleanup(patcher_openro.stop)
        self.addCleanup(patcher_conn.stop)
        self.loader = MockConfigurationLoader(conf)
        self.tbd = Cloubed(conf_loader=self.loader)

    def test_storage_pools(self):
        """Cloubed.storage_pools() should return the list of names of storage
           pools
        """

        self.assertEquals(self.tbd.storage_pools(), ['test_storage_pool',])

    def test_storage_volumes(self):
        """Cloubed.storage_volumes() should return the list of names of storage
           volumes
        """

        self.assertEquals(self.tbd.storage_volumes(),
                          ['test_storage_volume1', 'test_storage_volume2'])

    def test_networks(self):
        """Cloubed.networks() should return the list of names of networks"""

        self.assertEquals(self.tbd.networks(),
                          ['test_network1', 'test_network2'])

    def test_domains(self):
        """Cloubed.domains() should return of names of domains"""

        self.assertEquals(self.tbd.domains(), ['test_domain1', 'test_domain2'])

    def test_get_domain_by_name(self):
        """Cloubed.get_domain_by_name() shoud find the Domain with name in
           parameter and return it else raise CloubedException
        """

        self.assertIsInstance(self.tbd.get_domain_by_name('test_domain1'), Domain)
        self.assertRaisesRegexp(CloubedException,
                                'domain fail not found in configuration',
                                self.tbd.get_domain_by_name,
                                'fail')

    def test_get_domain_by_libvirt_name(self):
        """Cloubed.get_domain_by_libvirt_name() shoud find the Domain with
           libvirt name in parameter and return it else raise CloubedException
        """

        self.assertIsInstance(
            self.tbd.get_domain_by_libvirt_name("{user}:test_testbed:test_domain1" \
                                                  .format(user=getuser())),
            Domain)
        self.assertRaisesRegexp(CloubedException,
                                'domain fail not found in configuration',
                                self.tbd.get_domain_by_libvirt_name,
                                'fail')

    def test_get_network_by_name(self):
        """Cloubed.get_network_by_name() shoud find the Network with name in
           parameter and return it else raise CloubedException
        """

        self.assertIsInstance(self.tbd.get_network_by_name('test_network1'), Network)
        self.assertRaisesRegexp(CloubedException,
                                'network fail not found in configuration',
                                self.tbd.get_network_by_name,
                                'fail')

    def test_get_storage_volume_by_name(self):
        """Cloubed.get_storage_volume_by_name() shoud find the StorageVolume
           with name in parameter and return it else raise CloubedException
        """

        self.assertIsInstance(self.tbd.get_storage_volume_by_name('test_storage_volume1'), StorageVolume)
        self.assertRaisesRegexp(CloubedException,
                                'storage volume fail not found in configuration',
                                self.tbd.get_storage_volume_by_name,
                                'fail')

    def test_get_storage_pool_by_name(self):
        """Cloubed.get_storage_pool_by_name() shoud find the StoragePool
           with name in parameter and return it else raise CloubedException
        """

        self.assertIsInstance(self.tbd.get_storage_pool_by_name('test_storage_pool'), StoragePool)
        self.assertRaisesRegexp(CloubedException,
                                'storage pool fail not found in configuration',
                                self.tbd.get_storage_pool_by_name,
                                'fail')

    def test_get_templates_dict(self):
        """Cloubed.get_templates_dict() shoud return a dict with all parameters
           in configuration but if the domain name given in parameter could not
           be found a CloubedException should be raised
        """

        self.maxDiff = None
        d1 = self.tbd.get_templates_dict('test_domain1')
        d2 = {'self.name': 'test_domain1',
              'testbed': 'test_testbed' }
        self.assertTrue(set(d2.items()).issubset(set(d1.items())))

        self.assertRaisesRegexp(CloubedException,
                                'domain fail not found in configuration',
                                self.tbd.get_templates_dict,
                                'fail')

    def test_boot_vm(self):
        """Cloubed.boot_vm() shoud run without trouble
        """

        self.tbd.boot_vm('test_domain1')
        self.tbd.boot_vm('test_domain1',
                         overwrite_disks=True,
                         recreate_networks=True)
        self.tbd.boot_vm('test_domain2')

    def test_shutdown(self):
        """Cloubed.shutdown() shoud run without trouble
        """

        domain = 'test_domain1'
        self.tbd.boot_vm(domain)
        self.tbd.shutdown(domain)

    def test_destroy(self):
        """Cloubed.destroy() shoud run without trouble
        """

        domain = 'test_domain1'
        self.tbd.boot_vm(domain)
        self.tbd.destroy(domain)

    def test_reboot(self):
        """Cloubed.reboot() shoud run without trouble
        """

        domain = 'test_domain1'
        self.tbd.boot_vm(domain)
        self.tbd.reboot(domain)

    def test_reset(self):
        """Cloubed.reset() shoud run without trouble
        """

        domain = 'test_domain1'
        self.tbd.boot_vm(domain)
        self.tbd.destroy(domain)

    def test_suspend(self):
        """Cloubed.suspend() shoud run without trouble
        """

        domain = 'test_domain1'
        self.tbd.boot_vm(domain)
        self.tbd.suspend(domain)

    def test_resume(self):
        """Cloubed.resume() shoud run without trouble
        """

        domain = 'test_domain1'
        self.tbd.boot_vm(domain)
        self.tbd.resume(domain)

    def test_get_infos(self):
        """Cloubed.get_infos() shoud run without trouble
        """

        self.tbd.boot_vm('test_domain1')
        self.tbd.boot_vm('test_domain2')
        self.tbd.get_infos()

    def test_cleanup(self):
        """Cloubed.cleanup() shoud run without trouble
        """

        self.tbd.boot_vm('test_domain1')
        self.tbd.cleanup()

    def test_xml(self):
        """Cloubed.xml() shoud run without trouble except if the type of
           resource is not valid and CloubedException should be raised
        """

        self.tbd.xml('domain','test_domain2')
        self.tbd.xml('network','test_network2')
        self.tbd.xml('storagevolume','test_storage_volume2')
        self.tbd.xml('storagepool','test_storage_pool')
        self.assertRaisesRegexp(CloubedException,
                                "cannot dump XML of invalid resource type fail",
                                self.tbd.xml,
                                'fail', 'test_fail')

loadtestcase(TestCloubed)
