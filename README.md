ClouBed
=======

ClouBed is a python library that intends to help you create and manage *virtual
testbeds*. ClouBed basically stands for « CLOUd testBED ».

The big picture is: programmable Vagrant on multiple KVM.

ClouBed embraces all the power of libvirt for managing the whole infrastructure
of your virtual testbed (storage pools, disks, networks, events) through a
simple YAML file to describe your distributed setup.

The API of the library lets you write simple scripts to automate the management
of the KVM virtual machines in your testbed.

Licence
-------

ClouBed is distributed under the terms of the GNU Lesser General Public License
version 3.

Documentation
-------------

There is not yet documentation at this time. It is advised to have a look at the
available examples as a starting point in the meantime.

Requirements
------------

It only works on GNU/Linux systems with KVM.

* Python >= 2.7 (not tested with previous versions)
* libvirt with its python binding >= 0.9.12 (not tested with previous versions)
* PyYAML >= 3.10 (not tested with previous versions)

Installation
------------

### on Debian/Ubuntu

First, install all packages dependancies:

```sh
sudo apt-get install python-libvirt python-yaml qemu-utils kvm
```

Then load the kernel module for hardware virtualization instruction set support:

* for Intel CPU:

```sh
sudo modprobe kvm-intel
```

* for AMD CPU:

```sh
sudo modprobe kvm-amd
```

Become a member of `libvirtd` system group:

```sh
sudo adduser $USER libvirtd
```

Git clone this repository,

Then export environment variable `$PYTHONPATH` with ClouBed `lib/` directory in
order to let Python find `cloubed` module.

#### on CentOS/Fedora

Soon.

Disclaimer
----------

Please note that this software is far from being reliable and well suited for
many users and developers. As of now, it should probably only fit to the needs
of its main author (which is already cool from his standpoint). One last thing
to keep mind: the API will change in future releases, there is just no chance
for the opposite.

If you are still here after reading this, I guess you are masochist. But that
is cool, I love receiving pull requests from masochists!
