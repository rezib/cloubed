Introduction
============

ClouBed is a python library that intends to help you create and manage *virtual
testbeds*. ClouBed basically stands for « CLOUd testBED ».

ClouBed embraces all the power of `libvirt`_ for managing the whole
infrastructure of your virtual testbed (storage pools, disks, networks, events)
through a simple YAML file to describe your distributed setup.

The API of the library lets you write simple scripts to automate the management
of the KVM virtual machines in your testbed.

.. _KVM: http://www.linux-kvm.org/
.. _libvirt: http://libvirt.org/

Use cases
---------

Cloubed may be helpful for these typical uses cases.

Comparaisons
------------

* `Vagrant`_
* `Packer`_
* `OpenStack`_
* `Ganeti`_

.. _Vagrant: http://www.vagrantup.com/
.. _Packer: http://www.packer.io/
.. _OpenStack: http://www.openstack.org/
.. _Ganeti: http://code.google.com/p/ganeti/

Licence
-------

ClouBed is distributed under the terms of the GNU Lesser General Public License
version 3.
