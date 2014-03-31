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

Usage
-----

### Utility

Here are somes examples of the usage of `cloubed` command.

* Show the current status of all resources declared in YAML file:

```sh
cloubed status
```

* Generate the file named `pxe` of domain `test` in YAML file using its template:

```sh
cloubed gen --domain=test --filename=pxe
```

* Boot the domain `test` with different optional parameters:

```
cloubed boot --domain=test
cloubed boot --domain=test --overwrite-disks=debian-vol
cloubed boot --domain=test --overwrite-disks=yes --recreate-networks=yes
cloubed boot --domain=test --bootdev=network
```

* Wait for the domain `test` to be stopped:

```sh
cloubed wait --domain=test --event=shutdown:stopped
```

* Destroy all resources:

```sh
cloubed cleanup
```

Try `cloubed --help` for more information about the usage of this command.

### Library

There is no real documentation yet on how-to use Cloubed library at this time. It
is planned to publish one soon though. In the meantime, it is advised to have a
look at the available examples in `examples/*` directories as a starting point.

Requirements
------------

It only works on GNU/Linux systems with KVM.

* Python >= 2.6
* libvirt with its python binding >= 0.9.12 (not tested with previous versions)
* PyYAML >= 3.10 (not tested with previous versions)

Installation
------------

Please refer to the [installation guide](http://cloubed.org/doc/installation.html)
in Cloubed [online documentation](http://cloubed.org/doc) for all installation
instructions.

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

Cloubed is not ready for production use since its user base is still very small.
But please open [a new issue](https://github.com/rezib/cloubed/issues/new) if you
encounter any problem or if you think a great feature is missing

Please note that both the API and YAML file format are likely to change in future
releases of Cloubed.
