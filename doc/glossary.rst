Glossary
========

Cloubed uses the terminology introduced in Libvirt. This aims for a better
coherency with its library/API and its software ecosystem. Since this
terminology is not totally intuitive though, this glossary may help users that
are not used to it.

.. glossary::

   node
      A single physical machine that runs domains.

   hypervisor
      A layer of software allowing to virtualize a node in a set of virtual
      machines with possibly different configurations than the node itself.
      Even if Libvirt goal is to support different hypervisors (eg. Xen, LXC,
      etc), Cloubed volontarily only relies on the Linux QEMU/KVM hypervisor.

   domain
      Basically, it is commonly a virtual machine. More precisely, it is an
      instance of an operating system running on a virtualized machine provided
      by the hypervisor.

   network
      A virtual component on the node on which the domain network interfaces
      will be connected. In Cloubed, it is a virtual Ethernet bridge.

   storage volume
      A single storage volume which can be assigned to a guest, or used for
      creating further pools. A volume is either a block device, a raw file, or
      a special format file. In Cloubed, only the last two options are supported
      though.

   storage pool
      It provides a means for taking a chunk of storage and carving it up into
      volumes. Potentially, a pool can be used to manage things such as a
      physical disk, a NFS server, a iSCSI target, a host adapter, an LVM group.
      In Cloubed, it is simply a POSIX directory that will contains the storage
      volumes though.

   resource
      Generic term to designate either a domain, network, storage volume or
      storage pool.
