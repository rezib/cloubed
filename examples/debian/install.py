#!/usr/bin/env python

from cloubed import cloubed
import logging

VM = "vmtest"

logging.basicConfig(format='%(levelname)-7s: %(message)s',
                            level=logging.DEBUG)

try:
    print("generating template file")
    cloubed.gen_file(domain_name = VM, template_name = "ipxe")
    cloubed.gen_file(domain_name = VM, template_name = "preseed")
    print("booting vm {vm}".format(vm=VM))
    cloubed.boot_vm(domain_name = VM,
                    bootdev = "network",
                    overwrite_storage_volume = True)
    print("waiting event shutdown on vm {vm}".format(vm=VM))
    cloubed.wait_event(VM, "STOPPED", "SHUTDOWN")
    print("booting vm {vm}".format(vm=VM))
    cloubed.boot_vm(VM)

except cloubed.CloubedException as cdb_error:
    print(cdb_error)
except KeyboardInterrupt:
    print("install script stopped.")
