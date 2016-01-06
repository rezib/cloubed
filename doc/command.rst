Cloubed command
===============

Synopsis
--------

**cloubed** [-h --help] [-c --conf *pathname*] [-d --debug] *action* *options* 

Description
-----------

Cloubed is a utility to help manage a testbed composed of one or multiple
virtual machines. It relies on Libvirt and QEMU/KVM virtualisation technologies.

Once the testbed components are described in a YAML file, Cloubed can be used to
easily create the virtual networks, disk images and boot the virtual machines in
an automated fashion.

Actions
-------

Available actions:

  boot
    Boot a domain and create all required resources.

  shutdown
    Shutdown gracefully a domain by sending the instruction to the OS through
    ACPI.

  destroy
    Shutdown instantly a domain without telling anything to the OS. It may
    cause data loss and corrupt the system.

  reboot
    Reboot gracefully a domain by sending the instruction to the OS through
    ACPI.

  reset
    Cold-reset a domain without telling anything to the OS. It may cause data
    loss and corrupt the system.

  suspend
    Suspend a domain into its RAM within ACPI S3 state.

  resume
    Resume a previously suspended domain.

  wait
    Wait for an event to occur on a domain.

  gen
    Generate files based on templates.

  xml
    Print the XML description of a resource as created in Libvirt.

  status
    Print the status of all resources of the testbed.

  vars
    Print variables usable in templates for a domain.

  cleanup
    Delete all existing resrouces of the testbed.


Global options
--------------

    -h, --help      Show help message and exit.
    -c FILE, --conf=FILE
                    Alternative testbed YAML file. Default is **./cloubed.yaml**.
    -d, --debug     Enable debug output.

Boot options
------------

Required arguments for `boot` action:

    --domain=DOMAIN  The domain name to boot.

Optional arguments for `boot` action:

    --bootdev=DEV
                    First boot device. Possible values are **hd**, **network**
                    or **cdrom**. Default is **hd**.
    --overwrite-disks=DISKS
                    Storage volumes to overwrite before booting. Possible values
                    are **yes** to overwrite all storage volumes of the domain,
                    **no** for none, or a list of storage volume names separated
                    by blank spaces. Default is **no**.
    --recreate-networks=NETWORKS
                    Networks to recreate before booting. Possible value are
                    **yes** to recreate all networks connected to the domain,
                    **no** for none, or a list of network names separated by
                    blank spaces. Default is **no**.

Shutdown options
----------------

Required arguments for `shutdown` action:

    --domain=DOMAIN  The domain name to boot.

Destroy options
---------------

Required arguments for `destroy` action:

    --domain=DOMAIN  The domain name to boot.

Reboot options
--------------

Required arguments for `reboot` action:

    --domain=DOMAIN  The domain name to boot.

Reset options
-------------

Required arguments for `reset` action:

    --domain=DOMAIN  The domain name to boot.

Suspend options
---------------

Required arguments for `suspend` action:

    --domain=DOMAIN  The domain name to boot.

Resume options
--------------

Required arguments for `resume` action:

    --domain=DOMAIN  The domain name to boot.

Wait options
------------

Required arguments for `wait` action:

    --domain=DOMAIN  The domain on which the event will occur.
    --event=EVENT    The event to wait for. The event should be supported by
                     Libvirt and it should be specified in the form
                     `type`:`detail`.
    --enable-http    Enable internal HTTP server. It is disabled by default.

Gen options
-----------

Required arguments for `gen` action:

    --domain=DOMAIN   The domain associated to the file to generate.
    --filename=FILE   The name of the file to generate.

Vars options
------------

Required arguments for `vars` action:

    --domain=DOMAIN  The domain of the variables to print.

Xml options
-----------

Required arguments for `xml` action:

    --resource=RES   The name of the resource to represent in XML. The resource
                     should be specified in the form `type`:`name` where `type`
                     is either **domain**, **network**, **storagevolume** or
                     **storagepool** and `name` is the name of the resource as
                     specified in YAML file.

Examples
--------

Boot domain *srv1*:

  cloubed boot --domain=srv1

Overwrite disks of domain *srv2* and boot it on its network devices:

  cloubed boot --domain=srv2 --overwrite-disks=yes --bootdev=network

Recreate networks connected to domain *srv3*, overwrite its disks *root* and
*backup*, boot it on its network devices and enable debug mode:

  cloubed --debug boot --domain=srv3 --recreate-networks=yes \
  --overwrite-disks root backup --bootdev=network

Generate file *ssh* of domain *node1* based on its template:

  cloubed gen --domain=node1 --file=ssh

Wait for the domain *node2* to shutdown:

  cloubed wait --domain=node2 --event=stopped:shutdown

Print the XML representation of network *backbone*:

  cloubed xml --resource=network:backbone

Print the variables that could be used in templates of domain *node1*:

  cloubed vars --domain=node1

Print the current status of all resources of the testbed:

  cloubed status
