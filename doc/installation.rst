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

From Sources
^^^^^^^^^^^^

Download the source tarball of the latest stable release on `Cloubed website`_
and extract it. Alternatively, you can also clone the Git repository `hosted
on Github`_.

Then run the install with::

    sudo python setup.py install

.. _Cloubed website: http://cloubed.org/pub/
.. _hosted on GitHub: http://github.com/rezib/cloubed

Debian/Ubuntu
^^^^^^^^^^^^^

Add Cloubed Debian repository in a new repository file (eg.
``/etc/apt/sources.list.d/cloubed.list``), with the following content::

    deb http://localhost/debian cloubed contrib

Update your package sources database::

    sudo apt-get update

Then, install Cloubed package::

    sudo apt-get install cloubed

Then load the kernel module for hardware virtualization instruction set support:

* for Intel CPU::

    sudo modprobe kvm-intel

* for AMD CPU::

    sudo modprobe kvm-amd

Become a member of ``libvirtd`` system group::

    sudo adduser $USER libvirtd

RHEL/CentOS/Fedora
^^^^^^^^^^^^^^^^^^

Add Cloubed Yum repository in a new repository file (eg.
``/etc/yum.repos.d/cloubed.repo``), with the following content::

    [cloubed]
    name=Cloubed upstream repository
    baseurl=http://cloubed.org/rpm
    enabled=1
    gpgcheck=0

Then install and enable EPEL repositories as explained in the `official EPEL
documentation`_.

.. _official EPEL documentation: http://fedoraproject.org/wiki/EPEL

Then install Cloubed package::

    sudo yum install cloubed

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
