Installation guide
==================

Requirements
------------

Cloubed software has the following dependencies:

* Python >= 2.6
* `PyYAML`_, a common Python library to parse YAML files
* `Libvirt`_ with its python binding >= 0.9.12
* `QEMU`_ with `KVM`_ support

Since Cloubed is designed to work specifically with KVM virtualization
technologies, it only works on GNU/Linux based operating systems.

.. _PyYAML: http://pyyaml.org/
.. _QEMU: http://wiki.qemu.org/Main_Page
.. _KVM: http://www.linux-kvm.org/page/Main_Page
.. _Libvirt: http://libvirt.org/

Installation
------------

Debian/Ubuntu
^^^^^^^^^^^^^

First, install all packages dependencies::

    sudo apt-get install python-libvirt python-yaml qemu-utils kvm

Then load the kernel module for hardware virtualization instruction set support:

* for Intel CPU::

    sudo modprobe kvm-intel

* for AMD CPU::

    sudo modprobe kvm-amd

Become a member of ``libvirtd`` system group::

    sudo adduser $USER libvirtd

Download and extract a copy of this repository and finally install ClouBed
Python package::

    sudo python setup.py install


CentOS/Fedora
^^^^^^^^^^^^^

First, install all packages dependencies from official distribution::

    sudo yum install libvirt libvirt-python qemu-kvm


Then, install PyYAML and argparse libraries from EPEL repository. Please refer
to the `official EPEL documentation`_ for instructions to add EPEL repository on
your system::

    sudo yum install python-yaml python-argparse # from EPEL

.. _official EPEL documentation: http://fedoraproject.org/wiki/EPEL 

Then configure libvirt to disable authentication. Please note that this is just
a proposal for a minimal configuration of libvirt daemon to work easily with
Cloubed. It may actually depends on your requirements regarding security. The
configuration of libvirt daemon is out-of-scope of this README file, please
refer to `libvirt official documentation`_ for more information.

Edit file ``/etc/libvirt/libvirtd.conf``::

    @@ -128,3 +128,3 @@
     # an authentication mechanism here
    -#auth_unix_ro = "none"
    +auth_unix_ro = "none"
    
    @@ -137,3 +137,3 @@
     # an authentication mechanism here
    -#auth_unix_rw = "none"
    +auth_unix_rw = "none"

.. _libvirt official documentation: http://libvirt.org/auth.html#ACL_server_config

Then start the libvirt daemon::

    sudo service libvirtd start

Download and extract a copy of this repository and finally install Cloubed
Python package::

    sudo python setup.py install