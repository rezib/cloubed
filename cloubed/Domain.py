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
import socket
from xml.dom.minidom import Document

from cloubed.CloubedException import CloubedException
from cloubed.DomainTemplate import DomainTemplate
from cloubed.DomainNetif import DomainNetif
from cloubed.DomainDisk import DomainDisk
from cloubed.DomainVirtfs import DomainVirtfs
from cloubed.Utils import getuser

class Domain:

    """ Domain class """

    def __init__(self, tbd, domain_conf):

        self.tbd = tbd
        self.ctl = self.tbd.ctl
        self._virtobj = None
        self.name = domain_conf.name

        use_namespace = True # should better be a conf parameter in the future
        if use_namespace:    # logic should moved be in an abstract parent class
            self.libvirt_name = \
                "{user}:{testbed}:{name}" \
                    .format(user = getuser(),
                            testbed = domain_conf.testbed,
                            name = self.name)
        else:
            self.libvirt_name = self.name

        self.vcpu = domain_conf.sockets * domain_conf.cores * domain_conf.threads
        self.sockets = domain_conf.sockets
        self.cores = domain_conf.cores
        self.threads = domain_conf.threads

        self.memory = domain_conf.memory

        self.netifs = []
        # ex: [ 'admin', 'backbone' ]
        for netif in domain_conf.netifs:
            netif = DomainNetif(self.tbd, self.name, netif)
            self.netifs.append(netif)

        self.disks = []
        for disk in domain_conf.disks:
            self.disks.append(DomainDisk(self.tbd, disk))

        self.cdrom = domain_conf.cdrom

        self.virtfs = [ DomainVirtfs(virtfs["source"], virtfs["target"]) \
                        for virtfs in domain_conf.virtfs ]

        self.bootdev = None # defined at boot time
        self.graphics = domain_conf.graphics

        self.templates = []
        for template_conf in domain_conf.template_files:
            self.templates.append(DomainTemplate(template_conf))

        self._events = []
        self._doc = None

        self._lock = threading.Lock()

    #
    # accessors
    #

    def get_storage_volumes(self):

        """ Returns the list of storage volume of the Domain """

        return [ disk.storage_volume for disk in self.disks ]

    def get_storage_volumes_names(self):

        """ Returns the list of storage volume names of the Domain """

        return [ disk.get_storage_volume_name() for disk in self.disks ]

    def get_networks(self):

        """ Returns the list of network of the Domain """

        return [ netif.network for netif in self.netifs ]

    def get_networks_names(self):

        """ Returns the list of network names of the Domain """

        return [ netif.get_network_name() for netif in self.netifs ]

    def get_infos(self):
        """Returns a dict full of key/value string pairs with information about
           the Domain.
        """
        return self.ctl.info_domain(self.libvirt_name)

    def get_template_by_name(self, template_name):

        """ Returns the DomainTemplate with this name """

        for template in self.templates:
            if template.name == template_name:
                return template

        # template not found therefore raise exception
        raise CloubedException(
                  "template {template} not defined for domain {domain}" \
                      .format(template = template_name,
                              domain = self.name))

    def get_first_host_ip(self):
        """Returns the first host ip addresses found in on all networks
           connected to the domain or None if not found.
        """

        list_ip_hosts = [ dom_netif.network.ip_host \
                          for dom_netif in self.netifs \
                          if dom_netif.network.ip_host \
                             is not None ]
        if len(list_ip_hosts) > 0:
            return list_ip_hosts[0]
        return None

    def xml(self):

        """ Returns the libvirt XML representation of the Domain """

        self.__init_xml()
        return self._doc

    def toxml(self):

        """ Returns the libvirt XML representation of the Domain as string """

        return self.xml().toxml()

    def created(self):

        """ Returns True if the Domain has been created in libvirt """

        return self._virtobj is not None

    def create(self,
               bootdev='hd'):

        """ Creates the Domain """

        domain = self.ctl.find_domain(self.libvirt_name)
        if domain:
            if domain.isActive():
                logging.info("destroying domain {name}" \
                                 .format(name=self.libvirt_name))
                domain.destroy()
            else:
                logging.info("undefining domain {name}" \
                                 .format(name=self.libvirt_name))
                domain.undefine()

        self.bootdev = bootdev

        # create the domain
        self.ctl.create_domain(self.toxml())
        logging.info("domain {domain}: created".format(domain=self.name))

    def shutdown(self):

        """ Shutdown the domain """

        domain = self.ctl.find_domain(self.libvirt_name)
        if domain is None:
            logging.warning("unable to shutdown domain {name} since not " \
                            "found in libvirt".format(name=self.name))
            return
        self.ctl.shutdown_domain(self.libvirt_name)
        logging.info("domain {domain}: shutdown".format(domain=self.name))

    def destroy(self):

        """
            Destroys the Domain in libvirt
        """

        domain = self.ctl.find_domain(self.libvirt_name)
        if domain is None:
            logging.debug("unable to destroy domain {name} since not found " \
                          "in libvirt".format(name=self.name))
            return # do nothing and leave
        if domain.isActive():
            logging.warn("destroying domain {name}".format(name=self.name))
            domain.destroy()
        else:
            logging.warn("undefining domain {name}".format(name=self.name))
            domain.undefine()

    def reboot(self):

        """ Gracefully reboot the domain """

        domain = self.ctl.find_domain(self.libvirt_name)
        if domain is None:
            logging.warning("unable to reboot domain {name} since not " \
                            "found in libvirt".format(name=self.name))
            return
        self.ctl.reboot_domain(self.libvirt_name)
        logging.info("domain {domain}: reboot".format(domain=self.name))

    def reset(self):

        """ Cold-reset the domain """

        domain = self.ctl.find_domain(self.libvirt_name)
        if domain is None:
            logging.warning("unable to reset domain {name} since not " \
                            "found in libvirt".format(name=self.name))
            return
        self.ctl.reset_domain(self.libvirt_name)
        logging.info("domain {domain}: reset".format(domain=self.name))

    def suspend(self):

        """ Suspend-to-RAM (ACPI S3 state) the domain """

        domain = self.ctl.find_domain(self.libvirt_name)
        if domain is None:
            logging.warning("unable to suspend domain {name} since not " \
                            "found in libvirt".format(name=self.name))
            return
        self.ctl.suspend_domain(self.libvirt_name)
        logging.info("domain {domain}: suspend".format(domain=self.name))

    def resume(self):

        """ Resume the domain from suspended state """

        domain = self.ctl.find_domain(self.libvirt_name)
        if domain is None:
            logging.warning("unable to resume domain {name} since not " \
                            "found in libvirt".format(name=self.name))
            return
        self.ctl.resume_domain(self.libvirt_name)
        logging.info("domain {domain}: resume".format(domain=self.name))

    def notify_event(self, event):

        """ notify_event: used to notify a Domain about a DomainEvent """

        logging.debug("domain {domain}: notified with event {event}" \
                          .format(domain=self.name, event=event))
        self._lock.acquire()        
        logging.debug("domain {domain}: lock acquired by notifyEvent" \
                          .format(domain=self.name))
        self._events.append(event)
        self._lock.release()
        logging.debug("domain {domain}: lock released by notifyEvent" \
                          .format(domain=self.name))

    def wait_for_event(self, event):

        """
            wait_for_event: used to wait until the Domain is notified with the
            appropriate DomainEvent
        """

        logging.debug("domain {domain}: entering in wait_for_event loop" \
                      " waiting for event {event}" \
                      .format(domain=self.name,
                              event=event))

        while True:
            self._lock.acquire()        
            #logging.debug("domain {domain}: lock acquired by waitForEvent" \
            #                  .format(domain=self.name))
            for loop_event in self._events:
                if loop_event == event:
                    logging.info("domain {domain}: waited event {event}" \
                                 " found!" \
                                      .format(domain=self.name,
                                              event=loop_event))
                    self._lock.release()
                    return
                else:
                    logging.info("domain {domain}: removing needless event" \
                                 " {event}" \
                                      .format(domain=self.name,
                                              event=loop_event))
                    self._events.remove(loop_event)
            self._lock.release()
            #logging.debug("domain {domain}: lock released by waitForEvent" \
            #                  .format(domain=self.name))
            time.sleep(1)

    def wait_tcp_socket(self, port):
        """Wait infinitely until TCP socket is open on port in parameter on the
           first static IP address of the domain. This method raises a
           CloubedException if the domain has not any static IP address in
           configuration. The port in parameter must be an integer and a valid
           TCP port number (in range 0-65535).
        """

        ips = [ netif.ip for netif in self.netifs \
                         if netif.ip is not None ]
        if len(ips) == 0:
            raise CloubedException("unable to wait for TCP socket since " \
                                   "domain {name} does not have any static " \
                                   "IP address".format(name=self.name))

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # set socket timeout to 1 second to avoid endless blocking
        # socket.connect() call
        sock.settimeout(1)
        firstip = ips[0]
        while True:
            logging.debug("trying to connect to TCP socket {ip}:{port}" \
                          .format(ip=firstip, port=port))
            try:
                sock.connect((firstip, port))
            except socket.error, msg:
                logging.debug("TCP error: {error}".format(error=msg))
                time.sleep(1)
                continue
            except socket.timeout, msg:
                logging.debug("TCP timeout: {error}".format(error=msg))
                continue
            break

    def __init_xml(self):

        """
            __init_xml: Translate the Domain to the libvirt XML representation
        """

        self._doc = Document()

        # <domain type='kvm'>
        #   <name>test-libvirt</name>
        #   <memory unit='GiB'>2</memory>
        #   <vcpu>2</vcpu>
        #   <cpu mode='host-model'>
        #     <model fallback='allow'/>
        #     <feature policy='optional' name='vmx'/>
        #     <topology sockets='1' cores='2' threads='1'/>
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
        #     <disk type='file' device='cdrom'>
        #       <source file='/home/user/boot.iso'/>
        #       <target dev='hdc' bus='ide'/>
        #       <readonly/>
        #     </disk>
        #     <filesystem type='mount' accessmode='passthrough'>
        #       <source dir='/export/to/guest'/>
        #       <target dir='/import/from/host'/>
        #       <readonly/>
        #     </filesystem>
        #     <interface type="network">
        #       <source network="network-name"/>
        #       <mac address="00:16:3e:75:40:d5"/>
        #       <model type="virtio"/>
        #     </interface>
        #     <graphics type='sdl'/>
        #     <graphics type='spice' />
        #     <serial type='pty'>
        #       <target port='0'/>
        #     </serial>
        #     <console type='pty'>
        #       <target type='serial' port='0'/>
        #     </console>
        #   </devices>
        # </domain>

        # root: domain
        element_domain = self._doc.createElement("domain")
        element_domain.setAttribute("type", "kvm")
        self._doc.appendChild(element_domain)

        # name 
        element_name = self._doc.createElement("name")
        node_name = self._doc.createTextNode(self.libvirt_name)
        element_name.appendChild(node_name)
        element_domain.appendChild(element_name)
        
        # memory
        element_memory = self._doc.createElement("memory")
        element_memory.setAttribute("unit", "MiB")
        node_memory = self._doc.createTextNode(str(self.memory))
        element_memory.appendChild(node_memory)
        element_domain.appendChild(element_memory)
        
        # vcpu
        element_vcpu = self._doc.createElement("vcpu")
        node_vcpu = self._doc.createTextNode(str(self.vcpu))
        element_vcpu.appendChild(node_vcpu)
        element_domain.appendChild(element_vcpu)

        # cpu
        element_cpu = self._doc.createElement("cpu")
        element_cpu.setAttribute("mode", "host-model")
        element_domain.appendChild(element_cpu)

        # cpu/model
        element_model = self._doc.createElement("model")
        element_model.setAttribute("fallback", "allow")
        element_cpu.appendChild(element_model)

        # cpu/topology
        element_topology = self._doc.createElement("topology")
        element_topology.setAttribute("sockets", str(self.sockets))
        element_topology.setAttribute("cores", str(self.cores))
        element_topology.setAttribute("threads", str(self.threads))
        element_cpu.appendChild(element_topology)

        # os
        element_os = self._doc.createElement("os")
        element_domain.appendChild(element_os)

        # os/type
        element_type = self._doc.createElement("type")
        node_type = self._doc.createTextNode("hvm")
        element_type.appendChild(node_type)
        element_os.appendChild(element_type)

        # os/boot
        if self.bootdev is not None:
            element_boot = self._doc.createElement("boot")
            element_boot.setAttribute("dev", self.bootdev)
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

        # hard disk

        for disk in self.disks:
            # devices/disk
            element_disk = self._doc.createElement("disk")
            element_disk.setAttribute("type", "file")
            element_disk.setAttribute("device", "disk")
            element_devices.appendChild(element_disk)
    
            # devices/disk/source
            element_source = self._doc.createElement("source")
            element_source.setAttribute("file",
                                        disk.storage_volume.getpath())
            element_disk.appendChild(element_source)
    
            # devices/disk/target
            element_target = self._doc.createElement("target")
            element_target.setAttribute("dev", disk.device)
            element_target.setAttribute("bus", disk.bus)
            element_disk.appendChild(element_target)
           
            # devices/disk/driver
            element_driver = self._doc.createElement("driver")
            element_driver.setAttribute("name", "qemu")
            element_driver.setAttribute("type", "qcow2")
            element_disk.appendChild(element_driver)

        # cdrom

        # devices/disk
        element_disk = self._doc.createElement("disk")
        if self.cdrom:
            element_disk.setAttribute("type", "file")
        else:
            element_disk.setAttribute("type", "block")
        element_disk.setAttribute("device", "cdrom")
        element_devices.appendChild(element_disk)

        if self.cdrom:
            # devices/disk/source
            element_source = self._doc.createElement("source")
            element_source.setAttribute("file", self.cdrom)
            element_disk.appendChild(element_source)
        else:
            # devices/disk/driver
            element_driver = self._doc.createElement("driver")
            element_driver.setAttribute("name", "qemu")
            element_driver.setAttribute("type", "raw")
            element_disk.appendChild(element_driver)

        # devices/disk/target
        element_target = self._doc.createElement("target")
        element_target.setAttribute("dev", "hdc")
        element_target.setAttribute("bus", "ide")
        if not self.cdrom:
            element_target.setAttribute("tray", "open")
        element_disk.appendChild(element_target)

        # devices/disk/readonly
        element_readonly = self._doc.createElement("readonly")
        element_disk.appendChild(element_readonly)

        # virtfs

        for fs in self.virtfs:

            # devices/filesystem
            element_fs = self._doc.createElement("filesystem")
            element_fs.setAttribute("type", "mount")
            #element_fs.setAttribute("accessmode", "passthrough")
            element_fs.setAttribute("accessmode", "mapped")
            element_devices.appendChild(element_fs)

            # devices/filesystem/source
            element_source = self._doc.createElement("source")
            element_source.setAttribute("dir", fs.source)
            element_fs.appendChild(element_source)

            # devices/filesystem/target
            element_target = self._doc.createElement("target")
            element_target.setAttribute("dir", fs.target)
            element_fs.appendChild(element_target)

        # netif 

        for netif in self.netifs:

            # devices/interface
            element_interface = self._doc.createElement("interface")
            element_interface.setAttribute("type", "network")
            element_devices.appendChild(element_interface)

            # devices/interface/source
            element_source = self._doc.createElement("source")
            element_source.setAttribute("network",
                                        netif.network.libvirt_name)
            element_interface.appendChild(element_source)

            # devices/interface/target
            #element_target = self._doc.createElement("target")
            #element_target.setAttribute("dev", "")
            #element_interface.appendChild(element_target)

            # devices/interface/mac
            element_mac = self._doc.createElement("mac")
            element_mac.setAttribute("address", netif.mac)
            element_interface.appendChild(element_mac)

            # devices/interface/model
            element_model = self._doc.createElement("model")
            element_model.setAttribute("type", "virtio")
            element_interface.appendChild(element_model)

        # devices/graphics
        if self.graphics:
            element_graphics = self._doc.createElement("graphics")
            element_graphics.setAttribute("type", self.graphics)
            # if spice is used, enable port auto-allocation
            if self.graphics == "spice":
                element_graphics.setAttribute("autoport", "yes")
            element_devices.appendChild(element_graphics)

        # serial console

        # devices/serial
        element_serial = self._doc.createElement("serial")
        element_serial.setAttribute("type", "pty")
        element_devices.appendChild(element_serial)

        # devices/serial/target
        element_target = self._doc.createElement("target")
        element_target.setAttribute("port", "0")
        element_serial.appendChild(element_target)

        # devices/console
        element_console = self._doc.createElement("console")
        element_console.setAttribute("type", "pty")
        element_devices.appendChild(element_console)

        # devices/console/target
        element_target = self._doc.createElement("target")
        element_target.setAttribute("type", "serial")
        element_target.setAttribute("port", "0")
        element_console.appendChild(element_target)
