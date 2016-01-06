Cloubed API
===========

.. py:function:: storage_pools()

   Returns the list of storage pools names.

   :exception CloubedConfigurationException:
       * ``cloubed.yaml`` file could not be found or read in current directory

.. py:function:: storage_volumes()

   Returns the list of storage volumes names.

   :exception CloubedConfigurationException:
       * ``cloubed.yaml`` file could not be found or read in current directory

.. py:function:: networks()

   Returns the list of networks names.

   :exception CloubedConfigurationException:
       * ``cloubed.yaml`` file could not be found or read in current directory

.. py:function:: domains()

   Returns the list of domains names.

   :exception CloubedConfigurationException:
       * ``cloubed.yaml`` file could not be found or read in current directory

.. py:function:: gen(domain, template)

   Generates the file `template` of the domain `domain` based on its template.

   :param string domain: domain name in the YAML file
   :param string template: template name for this domain in the YAML file
   :exception CloubedConfigurationException:
       * ``cloubed.yaml`` file could not be found or read in current directory
   :exception CloubedException:
       * the domain is not found in the YAML file
       * the template file is not found in the YAML file for this domain
       * the template input file could not be read or does not exist
       * the output file could not we written

.. py:function:: boot(domain, bootdev="hd", overwrite_disks=[], recreate_networks=[])

   Boot the domain `domain`. It also automatically checks that all its
   dependencies (networks, storage volumes and so on) already exist and create
   them if necessary.

   :param string domain: domain name in the YAML file
   :param string bootdev: Set the first boot device of the domain. See details
       below.
   :param overwrite_disks: disks of the domain to overwrite before booting it.
       See details below.
   :type overwrite_disks: boolean or list of strings
   :param recreate_networks: networks connected to the domain to recreate before
       booting it. See details below.
   :type recreate_networks: boolean or list of strings

   The optional parameter `bootdev` accepts the following values:

   * ``hd`` *(default)*: boot on attached block devices
   * ``network``: boot with PXE on network interfaces

   This parameter simply controls the type of the devices on which the
   domain will **firstly** tries to boot on. It will tries to boot on
   **all** devices of this type. For instance with ``hd``, a domain
   attached to two block devices will try sequentially to boot on these two
   attached block devices. But if it fails to boot on all devices of this
   specified type, it will then fallback on all other availables types of
   devices.

   The optional parameter `overwrite_disks` accepts the following values:

   * A list of storage volume names attached to the domain. For each
     volume, if it already exists, Cloubed will delete and recreate it
     from scratch before booting the domain. All previously existing
     partitions and data will therefore be **definitely lost**.
   * A boolean value:
       * ``False`` is equivalent to an empty list of storage volume.
       * ``True`` is equivalent to the list of **all** storage volumes attached to
         the domain.

   If no value is given, its default value is an empty list (or ``False``).

   The optional parameter `recreate_networks` accepts the following values:

   * A list of network names connected to the domain. For each network,
     if it already exists, Cloubed will delete and recreate it before
     booting the domain. Beware that If another domain is connected to
     the deleted network, it will lost its connection to this network.
   * A boolean value:
       * ``False`` is equivalent to an empty list of networks.
       * ``True`` is equivalent to the list of **all** networks
         connected to the domain.

   If no value is given, its default value is an empty list (or ``False``).

   :exception CloubedConfigurationException:
       * ``cloubed.yaml`` file could not be found or read in current directory
   :exception CloubedException:
       * the domain is not found in the YAML file
       * the specified `bootdev` does not exists
       * at least one of the disks to overwrite is not found in the YAML file
         for this domain
       * at least one of the network to recreate is not found in the YAML file
         for this domain

.. py:function:: shutdown(domain)

   Shutdown gracefully the domain `domain` by sending the corresponding ACPI
   instruction to the guest OS.

   :param string domain: domain name in the YAML file
   :exception CloubedConfigurationException:
       * ``cloubed.yaml`` file could not be found or read in current directory
   :exception CloubedException:
       * the domain is not found in the YAML file

.. py:function:: destroy(domain)

   Destroy immediatelly the domain `domain` without telling anything to the
   guest OS. This may cause data loss and corrupt the system.

   :param string domain: domain name in the YAML file
   :exception CloubedConfigurationException:
       * ``cloubed.yaml`` file could not be found or read in current directory
   :exception CloubedException:
       * the domain is not found in the YAML file

.. py:function:: reboot(domain)

   Reboot gracefully the domain `domain` by sending the corresponding ACPI
   instruction to the guest OS.

   :param string domain: domain name in the YAML file
   :exception CloubedConfigurationException:
       * ``cloubed.yaml`` file could not be found or read in current directory
   :exception CloubedException:
       * the domain is not found in the YAML file

.. py:function:: reset(domain)

   Cold-reset immediatelly the domain `domain` without telling anything to the
   guest OS. This may cause data loss and corrupt the system.

   :param string domain: domain name in the YAML file
   :exception CloubedConfigurationException:
       * ``cloubed.yaml`` file could not be found or read in current directory
   :exception CloubedException:
       * the domain is not found in the YAML file

.. py:function:: suspend(domain)

   Suspend to RAM the domain `domain` within ACPI S3 mode.

   :param string domain: domain name in the YAML file
   :exception CloubedConfigurationException:
       * ``cloubed.yaml`` file could not be found or read in current directory
   :exception CloubedException:
       * the domain is not found in the YAML file

.. py:function:: resume(domain)

   Resume a previously suspended domain `domain`.

   :param string domain: domain name in the YAML file
   :exception CloubedConfigurationException:
       * ``cloubed.yaml`` file could not be found or read in current directory
   :exception CloubedException:
       * the domain is not found in the YAML file

.. py:function:: create_network(network_name, recreate)

   Creates the network `network_name`.

   :param string network_name: network name in the YAML file
   :param boolean recreate: if ``True`` and the network already exists, it will
       be deleted and re-created. If ``False`` and the network already exists,
       it will stay as is.
   :exception CloubedConfigurationException:
       * ``cloubed.yaml`` file could not be found or read in current directory
   :exception CloubedException:
       * the network is not found in the YAML file

.. py:function:: cleanup()

   Destroys all existing resources.

   It also deletes all storage volumes and their data will be **definitely
   lost**.

   :exception CloubedConfigurationException:
       * ``cloubed.yaml`` file could not be found or read in current directory

.. py:function:: wait(domain, event, detail, enable_http)

   Waits for the event `event`:`detail` to happen on the domain `domain`.

   :param string domain: domain name in the YAML file
   :param string event: the type of the waited event. This is either an event
       type as known by Libvirt or `tcp` to wait for a TCP socket to open.
   :param string detail: detail about the waited event. This is either an event
       detail as known by Libvirt or a TCP port number.
   :param bool enable_http: weither internal HTTP server should be enable or
        not. Default value is False, the HTTP server is disabled.

   :exception CloubedConfigurationException:
       * ``cloubed.yaml`` file could not be found or read in current directory
   :exception CloubedException:
       * the domain is not found in the YAML file
       * the event tuple type:detail is invalid
