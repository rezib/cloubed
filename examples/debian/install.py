#!/usr/bin/env python

import cloubed
import logging

VM = "vmtest"

logging.basicConfig(format='%(levelname)-7s: %(message)s',
                            level=logging.DEBUG)

try:
    print("generating template file")
    cloubed.gen(domain=VM, template="ipxe")
    cloubed.gen(domain=VM, template="preseed")
    print("booting vm {vm}".format(vm=VM))
    cloubed.boot(domain=VM,
                 bootdev="network",
                 overwrite_disks=True,
                 recreate_networks=True )
    print("waiting event shutdown on vm {vm}".format(vm=VM))
    cloubed.wait(VM, "STOPPED", "SHUTDOWN")
    print("booting vm {vm}".format(vm=VM))
    cloubed.boot(VM)

except cloubed.CloubedException as cdb_error:
    print(cdb_error)
except KeyboardInterrupt:
    print("install script stopped.")
