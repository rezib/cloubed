#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013 Rémi Palancher 
#
# This file is part of Cloubed.
#
# Cloubed is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# Cloubed is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with Cloubed.  If not, see
# <http://www.gnu.org/licenses/>.

""" Domain class of Cloubed """

import logging
import time
import threading
import libvirt
import hashlib
from xml.dom.minidom import Document

from DomainTemplate import DomainTemplate
from DomainSnapshot import DomainSnapshot
from DomainNetif import DomainNetif
from DomainDisk import DomainDisk

def gen_mac(salt):

    """
       Simple utility/function to generate a MAC address with the salt given in
       parameter
    """

    salted = hashlib.sha1(salt).hexdigest()[:6]
    mac = [ "00", "16", "3e" ]
    mac.extend((salted[:2], salted[2:4], salted[4:6]))
    return ':'.join(mac)

class Domain:

    """ Domain class """

    _domains = []

    def __init__(self, conn, domain_conf):

        self._conn = conn
        self._virtobj = None
        self._name = domain_conf.get_name()
        self._vcpu = domain_conf.get_cpu()
        self._with_vmx = True # needed for nested KVM
        self._cpu_vendor = "Intel"      # only for VMX
        self._cpu_model = "SandyBridge" # only for VMX
                                        # the list of available models can be
                                        # retrieved with command:
                                        # $ kvm -cpu ?
        self._memory = domain_conf.get_memory()

        self._netifs = []
        netifs_list = domain_conf.get_netifs_list()
        # ex: [ 'admin', 'backbone' ]
        for network_name in netifs_list:
            mac = gen_mac("{domain_name:s}-{network_name:s}" \
                              .format(domain_name=self._name,
                                      network_name=network_name))
            self._netifs.append(DomainNetif(mac, network_name))

        self._disks = []
        disks_dict = domain_conf.get_disks_dict()
        # ex: { 'sda': 'vol-admin', 'sdb': 'vol-array' ]
        for device, storage_volume_name in disks_dict.iteritems():
            self._disks.append(DomainDisk(device, storage_volume_name))

        self._bootdev = None # defined at boot time
        self._graphics = domain_conf.get_graphics()

        self._templates = []
        for template_conf in domain_conf.get_templates_list():
            self._templates.append(DomainTemplate(template_conf))

        self._events = []
        self._doc = None

        self._lock = threading.Lock()

        Domain._domains.append(self)

    def __del__(self):

        try:
            Domain._domains.remove(self)
        except ValueError:
            pass

    def __eq__(self, other): # needed for __del__

        return self._name == other.get_name()

    #
    # accessors
    #

    def get_name(self):

        """ get_name: Returns name of Domain """

        return self._name

    @classmethod
    def get_by_name(cls, name):

        """ Returns the Domain with this name """

        for domain in cls._domains:
            if domain.get_name() == name:
                return domain

        return None

    def get_template_by_name(self, template_name):

        """ Returns the DomainTemplate with this name """

        for template in self._templates:
            if template.get_name() == template_name:
                return template

        return None

    def toxml(self):

        """ Returns the libvirt XML representation of the Domain """

        return self._doc.toxml()

    def getvirtobj(self):

        """ Returns the libvirt object of the Domain """

        return self._virtobj

    def created(self):

        """ Returns True if the Domain has been created in libvirt """

        return self._virtobj is not None

    def create(self,
               bootdev='hd',
               overwrite_storage_volume=False,
               overwrite=False):

        """ Creates the Domain and all its dependancies in libvirt """

        for disk in self._disks:
            if not disk.get_storage_volume().created():
                disk.get_storage_volume().create(overwrite_storage_volume)

        for netif in self._netifs:
            if not netif.get_network().created():
                netif.get_network().create(True)

        if overwrite:
            # delete all existing domain
            for domain_name in self._conn.listDefinedDomains():
                if domain_name == self._name:
                    domain = self._conn.lookupByName(domain_name)
                    logging.info("undefining domain " + domain_name)
                    domain.undefine()
            for domain_id in self._conn.listDomainsID():
                domain_name = self._conn.lookupByID(domain_id).name()
                if domain_name == self._name:
                    domain = self._conn.lookupByName(domain_name)
                    logging.info("destroying domain " + domain_name)
                    domain.destroy()

        self._bootdev = bootdev
        self.__init_xml()

        # create the domain
        self._virtobj = self._conn.createXML(self.toxml(), 0)
        logging.info("domain {domain}: created".format(domain=self._name))

    def notify_event(self, event):

        """ notify_event: used to notify a Domain about a DomainEvent """

        logging.debug("domain {domain}: notified with event {event}" \
                          .format(domain = self._name, event = event))
        self._lock.acquire()        
        logging.debug("domain {domain}: lock acquired by notifyEvent" \
                          .format(domain=self._name))
        self._events.append(event)
        self._lock.release()
        logging.debug("domain {domain}: lock released by notifyEvent" \
                          .format(domain=self._name))

    def wait_for_event(self, event):

        """
            wait_for_event: used to wait until the Domain is notified with the
            appropriate DomainEvent
        """

        logging.debug("domain {domain}: entering in wait_for_event loop" \
                      " waiting for event {event}" \
                      .format(domain=self._name,
                              event=event))

        while True:
            self._lock.acquire()        
            #logging.debug("domain {domain}: lock acquired by waitForEvent" \
            #                  .format(domain=self._name))
            for loop_event in self._events:
                if loop_event == event:
                    logging.info("domain {domain}: waited event {event}" \
                                 " found!" \
                                      .format(domain=self._name,
                                              event=loop_event))
                    self._lock.release()
                    return
                else:
                    logging.info("domain {domain}: removing needless event" \
                                 " {event}" \
                                      .format(domain=self._name,
                                              event=loop_event))
                    self._events.remove(loop_event)
            self._lock.release()
            #logging.debug("domain {domain}: lock released by waitForEvent" \
            #                  .format(domain=self._name))
            time.sleep(1)

    def snapshot(self, snapshot_name):

        """ snapshot: Make a snapshot of a Domain """

        domain_snapshot = DomainSnapshot(self._conn,
                                         snapshot_name,
                                         self._disks[0])
        self._virtobj = self._conn.lookupByName(self._name)
        self._virtobj.snapshotCreateXML(
                          domain_snapshot.toxml(),
                          libvirt.VIR_DOMAIN_SNAPSHOT_CREATE_DISK_ONLY)

    def __init_xml(self):

        """
            __init_xml: Translate the Domain to the libvirt XML representation
        """

        self._doc = Document()

        # <domain type='kvm'>
        #   <name>test-libvirt</name>
        #   <memory unit='GiB'>2</memory>
        #   <vcpu>2</vcpu>
        #   <cpu match='exact'>
        #     <model>SandyBridge</model>
        #     <feature policy='require' name='vmx'/>
        #   </cpu>
        #   <os>
        #     <type>hvm</type>
        #     <boot dev='network' />
        #   </os>
        #   <clock sync="localtime"/>
        #   <features>
        #     <acpi />
        #   </features>
        #   <on_poweroff>destroy</on_poweroff>
        #   <on_reboot>restart</on_reboot>
        #   <on_crash>restart</on_crash>
        #   <on_lockfailure>poweroff</on_lockfailure>
        #   <devices>
        #     <emulator>/usr/bin/kvm</emulator>
        #     <disk type='file' device='disk'>
        #       <source file='/absolute/path' />
        #       <target dev='sda' bus='virtio' />
        #       <driver name='qemu' type='qcow2' />
        #     </disk>
        #     <disk type='block' device='cdrom'>
        #       <driver name='qemu' type='raw' />
        #       <target dev='hdc' bus='ide' tray='open' />
        #       <readonly />
        #     </disk>
        #     <interface type='user'>
        #       <source network='network-name' />
        #       <target dev='eth0'/>
        #       <mac address='24:42:53:21:52:45' />
        #     </interface>
        #     <graphics type='sdl'/>
        #     <graphics type='spice' />
        #   </devices>
        # </domain>

        # root: domain
        element_domain = self._doc.createElement("domain")
        element_domain.setAttribute("type", "kvm")
        self._doc.appendChild(element_domain)

        # name 
        element_name = self._doc.createElement("name")
        node_name = self._doc.createTextNode(self._name)
        element_name.appendChild(node_name)
        element_domain.appendChild(element_name)
        
        # memory
        element_memory = self._doc.createElement("memory")
        element_memory.setAttribute("unit", "GiB")
        node_memory = self._doc.createTextNode(str(self._memory))
        element_memory.appendChild(node_memory)
        element_domain.appendChild(element_memory)
        
        # vcpu
        element_vcpu = self._doc.createElement("vcpu")
        node_vcpu = self._doc.createTextNode(str(self._vcpu))
        element_vcpu.appendChild(node_vcpu)
        element_domain.appendChild(element_vcpu)

        if self._with_vmx:

            # cpu
            element_cpu = self._doc.createElement("cpu")
            element_cpu.setAttribute("match", "exact")
            element_domain.appendChild(element_cpu)

            # cpu/model
            element_model = self._doc.createElement("model")
            node_model = self._doc.createTextNode(self._cpu_model)
            element_model.appendChild(node_model)
            element_cpu.appendChild(element_model)

            # cpu/vendor
            element_vendor = self._doc.createElement("vendor")
            node_vendor = self._doc.createTextNode(self._cpu_vendor)
            element_vendor.appendChild(node_vendor)
            element_cpu.appendChild(element_vendor)

            # cpu/feature
            element_feature = self._doc.createElement("feature")
            element_feature.setAttribute("policy", "require")
            element_feature.setAttribute("name", "vmx")
            element_cpu.appendChild(element_feature)

        # os
        element_os = self._doc.createElement("os")
        element_domain.appendChild(element_os)

        # os/type
        element_type = self._doc.createElement("type")
        node_type = self._doc.createTextNode("hvm")
        element_type.appendChild(node_type)
        element_os.appendChild(element_type)

        # os/boot
        if self._bootdev is not None:
            element_boot = self._doc.createElement("boot")
            element_boot.setAttribute("dev", self._bootdev)
            element_os.appendChild(element_boot)

        # clock
        element_clock = self._doc.createElement("clock")
        element_clock.setAttribute("sync", "localtime")
        element_domain.appendChild(element_clock)

        # features
        element_features = self._doc.createElement("features")
        element_domain.appendChild(element_features)

        # features/acpi
        element_acpi = self._doc.createElement("acpi")
        element_features.appendChild(element_acpi)
        
        # on_poweroff
        element_onpoweroff = self._doc.createElement("on_poweroff")
        node_onpoweroff = self._doc.createTextNode("destroy")
        element_onpoweroff.appendChild(node_onpoweroff)
        element_domain.appendChild(element_onpoweroff)

        # on_reboot
        element_onreboot = self._doc.createElement("on_reboot")
        node_onreboot = self._doc.createTextNode("restart")
        element_onreboot.appendChild(node_onreboot)
        element_domain.appendChild(element_onreboot)

        # on_crash
        element_oncrash = self._doc.createElement("on_crash")
        node_oncrash = self._doc.createTextNode("restart")
        element_oncrash.appendChild(node_oncrash)
        element_domain.appendChild(element_oncrash)

        # on_lockfailure
        element_onlockfailure = self._doc.createElement("on_lockfailure")
        node_onlockfailure = self._doc.createTextNode("poweroff")
        element_onlockfailure.appendChild(node_onlockfailure)
        element_domain.appendChild(element_onlockfailure)

        # devices
        element_devices = self._doc.createElement("devices")
        element_domain.appendChild(element_devices)

        # devices/emulator
        element_emulator = self._doc.createElement("emulator")
        node_emulator = self._doc.createTextNode("/usr/bin/kvm")
        element_emulator.appendChild(node_emulator)
        element_devices.appendChild(element_emulator)

        # hard disk

        for disk in self._disks:
            # devices/disk
            element_disk = self._doc.createElement("disk")
            element_disk.setAttribute("type", "file")
            element_disk.setAttribute("device", "disk")
            element_devices.appendChild(element_disk)
    
            # devices/disk/source
            element_source = self._doc.createElement("source")
            element_source.setAttribute("file",
                                        disk.get_storage_volume().getpath())
            element_disk.appendChild(element_source)
    
            # devices/disk/target
            element_target = self._doc.createElement("target")
            element_target.setAttribute("dev", disk.get_device())
            element_target.setAttribute("bus", "virtio")
            element_disk.appendChild(element_target)
           
            # devices/disk/driver
            element_driver = self._doc.createElement("driver")
            element_driver.setAttribute("name", "qemu")
            element_driver.setAttribute("type", "qcow2")
            element_disk.appendChild(element_driver)

        # cdrom

        # devices/disk
        element_disk = self._doc.createElement("disk")
        element_disk.setAttribute("type", "block")
        element_disk.setAttribute("device", "cdrom")
        element_devices.appendChild(element_disk)

        # devices/disk/driver
        element_driver = self._doc.createElement("driver")
        element_driver.setAttribute("name", "qemu")
        element_driver.setAttribute("type", "raw")
        element_disk.appendChild(element_driver)

        # devices/disk/target
        element_target = self._doc.createElement("target")
        element_target.setAttribute("dev", "hdc")
        element_target.setAttribute("bus", "ide")
        element_target.setAttribute("tray", "open")
        element_disk.appendChild(element_target)

        # devices/disk/readonly
        element_readonly = self._doc.createElement("readonly")
        element_disk.appendChild(element_readonly)

        # netif 

        for netif in self._netifs:

            # devices/interface
            element_interface = self._doc.createElement("interface")
            element_interface.setAttribute("type", "network")
            element_devices.appendChild(element_interface)

            # devices/interface/source
            element_source = self._doc.createElement("source")
            element_source.setAttribute("network",
                                        netif.get_network().get_name())
            element_interface.appendChild(element_source)

            # devices/interface/target
            #element_target = self._doc.createElement("target")
            #element_target.setAttribute("dev", "")
            #element_interface.appendChild(element_target)

            # devices/interface/mac
            element_mac = self._doc.createElement("mac")
            element_mac.setAttribute("address", netif.get_mac())
            element_interface.appendChild(element_mac)

            # devices/interface/model
            element_model = self._doc.createElement("model")
            element_model.setAttribute("type", "virtio")
            element_interface.appendChild(element_model)

        # devices/graphics
        if self._graphics:
            element_graphics = self._doc.createElement("graphics")
            element_graphics.setAttribute("type", self._graphics)
            # if spice is used, enable port auto-allocation
            if self._graphics == "spice":
                element_graphics.setAttribute("autoport", "yes")
            element_devices.appendChild(element_graphics)

