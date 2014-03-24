YAML file
=========

The description of your virtual testbed is entirely contained in a flat file in
the `YAML`_ format. YAML is the recursive acronym for *« YAML Ain't Markup
Language »*. It is basically a data serialization format which intends to be both
easy to read/write for humans and easy to parse by software.

.. _YAML: http://yaml.org/

Cloubed expects to find in a well-formated YAML file with a description of all
the resources which composes your testbed.

As of now, this YAML file should be named ``cloubed.yaml`` and it must be
located in the directory where the Cloubed software (either the command or the
library) will be used. The support of other file name and location will come in
future releases.

Here is an example of a minimal YAML file for Cloubed::

    testbed: foo
    storagepools:
      - name: foo-pool
        path: pool
    storagevolumes:
      - name: bar-vol
        storagepool: foo-pool
        size: 70
    networks:
      - name: foo-net
    domains:
      - name: bar
        cpu: 2
        memory: 1
        netifs:
          - network: foo-net
        disks:
          - device: sda
            storage_volume: bar-vol

It must contain these 5 required main sections: ``testbed``, ``storagepools``,
``storagevolumes``, ``networks`` and ``domains``. It may also contain an
optional ``templates`` section.

The ``testbed`` section only contains the name of the testbed. This name simply
has to be a valid string.

All the other sections of YAML file are described in the following sub-parts.

Storage pools
-------------

The ``storagepools`` section contains a list of storage pools or, in other
words, a list of places where will be stored the storage volumes of the testbed.
The parameters to define a storage pool are:

* ``name``: a valid string unique across all storage pools
* ``path``: path to an existing directory on the system. The path can be either
  absolute or relative to the directory where the YAML file is located. If the
  value starts with ``/``, an absolute path is presumed. If the directory does
  not exist on the system, Cloubed will raise an error when initializing the
  storage pool.

In the given minimal example, one storage pool is defined. Its name is
``foo-pool`` and its path is the ``pool/`` directory located in the same
directory as the YAML file.

Storage volumes
---------------

The ``storagevolumes`` section contains a list of storage volumes, *aka.* the
storage block devices used in the testbed. The parameters to define a storage
volume are:

* ``name``: a valid string unique across all storage volumes
* ``storagepool``: the name of the storage pool in which the volume will be
  created and stored. The storage pool must be defined in the dedicated section.
* ``size``: an integer representing the total size of the storage volume in
  gigabytes.
* ``format`` *(optional)*: the format of the storage volume file. It must be one
   of the formats supported by QEMU (see the the output of command
   ``qemu-img --help`` for the complete list). The default value is ``qcow2``
   and it should be appriopriate for most usages.

In the given minimal example, one storage volume is defined. Its name is
``bar-vol``, its size is 70GB and it will be stored in ``foo-pool`` storage
pool. Its format is the default ``qcow2``.

Networks
--------

The ``networks`` section contains a list of networks on which your domains can
be connected to. There is only one mandatory parameter:

* ``name``: a valid string unique accross all networks

Then, all other network parameters are optionals. They actually depend on the
forwarding mode of the network, among these three possibilities:

* Dedicated isolated bridge,
* Dedicated bridge with NAT routing enable,
* Shared existing bridge.

The choice between these network forwarding modes is controled by the following
parameter:

* ``forward`` *(optional)*: either ``none`` *(default)* for an isolated bridge,
  ``nat`` for a dedicated bridge with NAT routing enable or ``bridge`` for
  sharing an existing bridge.

Bridge forwarding mode
^^^^^^^^^^^^^^^^^^^^^^

In the ``bridge`` forwarding mode, the following parameter must also be defined:

* ``bridge`` *(optional)*: the name of the existing virtual bridge on the
  system. The list of existing virtual bridges can be retrieved with the command
  ``brctl show``.

Others forwarding modes
^^^^^^^^^^^^^^^^^^^^^^^

In both ``none`` and ``nat`` forwarding modes, the node virtual network
interface connected to dedicated bridge can be optionally configured with the
following parameters:

* ``ip_host`` *(optional)*: the IPv4 address of the node virtual network
  interface (eg. ``10.0.0.1``)
* ``network`` *(optional)*: the IPv4 netmask of the node virtual network
  interface (eg. ``255.255.255.0``)

These two parameters are globally optionals but they cannot be defined
separately. They must be either both defined or both undefined.

If the node virtual network interface is well configured, the DHCP service can
then be defined. This service is controled within a dedicated ``dhcp``
sub-section. When present, this sub-section must contain the following
parameters for defining the range of IPv4 addresses delivered by the DHCP
server:

* ``start`` *(optional)*: the first IPV4 address of the range (eg.
  ``10.0.0.100``). This must be a valid IPv4 address.
* ``end`` *(optional)*: the last IPV4 address of the range (eg. ``10.0.0.200``).
  This must be a valid IPv4 address numerically upper the ``start`` address.

These two parameters are globally optionals but they cannot be defined
separately. They must be either both defined or both undefined within the
``dhcp`` sub-section.

Finally, when DHCP service is properly enable, the PXE service can also be
defined. This service is controled within a dedicated ``pxe`` sub-section. When
present, this sub-section must contain the following parameters:

* ``tftp_dir`` *(optional)*: the path to the directory that contains your
  ``boot_file``. This path must be relative to the Cloubed YAML file.
* ``boot_file`` *(optional)*: the name of the boot file within the ``tftp_dir``.

These two parameters are globally optionals but they cannot be defined
separately. They must be either both defined or both undefined within the
``pxe`` sub-section. You may need to be familiar with `PXE concepts`_ to use
these advanced features.

.. _PXE concepts: http://en.wikipedia.org/wiki/Preboot_Execution_Environment

Examples
^^^^^^^^

Here are some commented examples of YAML ``networks`` sections valid for
Cloubed.

*Example 1*::

    networks:
      - name: foo1-net

There is one network named ``foo1-net`` with a dedicated isolated bridge.

*Example 2*::

    networks:
      - name: foo2-net
        forward: nat
        ip_host: 10.0.0.1
        netmask: 255.255.255.0
      - name: foo3-net
        forward: bridge
        bridge: br0

There are two networks. The ``foo2-net`` network is a dedicated bridge with NAT
routing enable. This means that domains with network interface can use the
``ip_host`` as a gateway for communicating with other IP networks outside of the
node (eg. the Internet). The ``foo3-net`` network will use the node virtual
bridge ``br0``. This bridge must be already existing on the node.

*Exemple 3*::

    networks:
      - name: foo4-net
        forward: nat
        ip_host: 10.1.0.1

        netmask: 255.255.255.0
        dhcp:
          start: 10.1.0.100
          end: 10.1.0.200
        pxe:
          tftp_dir: tftp
          boot_file: boot.ipxe

There is one ``foo4-net`` network with both DHCP and PXE services enable. The
DHCP server will attribute IPv4 address in the range from ``10.1.0.100`` to
``10.1.0.200``. The DHCP will provide ``boot.ipxe`` as the filename for a PXE
boot. Then, TFTP server will serve this file as soon as it is present in
``tftp/`` directory.

Domains
-------

The ``domains`` section contains the list of domains.
be connected to. Here is the list of basic mandatory parameters:

* ``name``: a valid string unique accross all domains
* ``cpu``: an integer representing the number of CPU for the domain
* ``memory``: either an integer representing the number of GiB of main memory
  for the domain or a string with an integer and a unit. Valid units are M, MB,
  MiB, G, GB and GIB.

Then, there are also 2 required sub-sections in a domain definition: ``netifs``
and ``disks``.

The sub-section ``netifs`` must contain a list of network interfaces for the
domain. Each network interface have the following parameters:

* ``network``: the name of the network the interface is connected to. This
  network must be defined previously in the dedicated section.
* ``ip`` *(optional)*: the IPv4 address that will be statically assigned to the
  interface (if the DHCP service is enable on the corresponding network).

The sub-section ``disks`` must contain a list of storage volumes for the
domain. Each storage volume must have the following parameters:

* ``device``: a valid string, the name of the device (not used yet).
* ``storage_volume``: the name of the storage volume. This storage volume must
  be defined previously in the dedicated section.

There is also an optional parameter for the domain:

* ``graphics`` *(optional)*: either ``spice`` or ``vnc``. If defined, the given
  protocol will be enable for remote access to the graphical console of the
  domain.

Optionally, the ``templates`` sub-section can also be defined to generate files
based on templates. If defined, this sub-section can contain:

* a ``files`` parameter which itself must contain a list of items with the
  following mandatory parameters:

  * ``name``: a valid string, the name of the template
  * ``input``: a valid string, either absolute or relative path to the input
    template file.
  * ``output``: a valid string, either absolute or relative path to the
    generated output file.

* a ``vars`` parameter which itself could contain arbitrary pairs of
  ``name: value`` parameters for future use in templates.

Examples
^^^^^^^^

Here is a simple but complete example of a ``domains`` section definition with
one ``admin`` domain::

    domains:
      - name: admin
        cpu: 2
        memory: 1
        netifs:
          - network: backbone
            ip: 10.5.0.1
        graphics: spice
        disks:
          - device: sda
            storage_volume: vol
        templates:
          files:
            - name: kickstart
              input: templates/host.ks
              output: http/host.ks
          vars:
            ntp: time.domain.tld

Templates
---------

The optional ``templates`` section can be defined to declare a list of global
template variables. When defined, it could contain arbitrary pairs of
``name: value`` variables. Here is an example of such section::

    templates:
      ntp_server: ntp.domain.tld
      dns: 8.8.8.8