Cloubed
=======

Cloubed is both a utility and a python library that intends to help you create
and manage *virtual testbeds*. Cloubed basically stands for « CLOUd testBED ».

The big picture is: programmable Vagrant on KVM.

Cloubed embraces all the power of libvirt for managing the whole infrastructure
of your virtual testbed (storage pools, disks, networks, events) through a
simple YAML file to describe your distributed setup.

The API of the library lets you write simple scripts to automate the management
of the KVM virtual machines in your testbed.

Licence
-------

Cloubed is distributed under the terms of the GNU Lesser General Public License
version 3.

Documentation
-------------

There is not yet documentation at this time. It is advised to have a look at the
available examples as a starting point in the meantime.

Requirements
------------

It only works on GNU/Linux systems with KVM.

* Python >= 2.6
* libvirt with its python binding >= 0.9.12 (not tested with previous versions)
* PyYAML >= 3.10 (not tested with previous versions)

Installation
------------

### Debian/Ubuntu

First, install all packages dependencies:

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

Download and extract a copy of this repository and finally install Cloubed
Python package:

```sh
sudo python setup.py install
```

#### CentOS/Fedora

First, install all packages dependencies from official distribution
repositories:

```sh
sudo yum install libvirt libvirt-python qemu-kvm
```

Then, install PyYAML and argparse libraries from EPEL repository. Please refer to
the [official EPEL documentation](http://fedoraproject.org/wiki/EPEL) for
instructions to add EPEL repository on your system:

```sh
sudo yum install python-yaml python-argparse # from EPEL
```

Then configure libvirt to disable authentication. Please note that this is just
a proposal for a minimal configuration of libvirt daemon to work easily with
Cloubed. It may actually depends on your requirements regarding security. The
configuration of libvirt daemon is out-of-scope of this README file, please
refer to
[libvirt official documentation](http://libvirt.org/auth.html#ACL_server_config)
for more information.

Edit file `/etc/libvirt/libvirtd.conf`:

```diff
@@ -128,3 +128,3 @@
 # an authentication mechanism here
-#auth_unix_ro = "none"
+auth_unix_ro = "none"

@@ -137,3 +137,3 @@
 # an authentication mechanism here
-#auth_unix_rw = "none"
+auth_unix_rw = "none"
```

Then start the libvirt daemon:

```sh
sudo service libvirtd start
```

Download and extract a copy of this repository and finally install Cloubed
Python package:

```sh
sudo python setup.py install
```

Troubleshooting
---------------

+ **dnsmasq: permission denied**

If you encounter the following error message when running Cloubed:

```
internal error Child process (/usr/sbin/dnsmasq
--conf-file=/var/lib/libvirt/dnsmasq/net.conf) unexpected exit status 3:
dnsmasq: TFTP directory /path/to/tftp/dir inaccessible: Permission denied
```

It actually means that `dnsmasq` daemon automatically launched by Libvirt for
TFTP and DHCP services is not able to access the `pxe>tftp_dir` specified in
your YAML file. The `dnsmasq` daemon is generally executed with UID `nobody`.
Try to `chmod` your directory (and recursively all its parents) so this process
can access your files.

Disclaimer
----------

Please note that this software is far from being reliable and well suited for
many users and developers. As of now, it should probably only fit to the needs
of its main author (which is already cool from his standpoint). One last thing
to keep mind: the API will change in future releases, there is just no chance
for the opposite.

If you are still here after reading this, I guess you are masochist. But that
is cool, I love receiving pull requests from masochists!
