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

.. py:function:: gen_file(domain_name, template_name)

   Generates the file `template_name` of the domain `domain_name` based on its
   template.

   :param string domain_name: domain name in the YAML file
   :param string template_name: template name for this domain in the YAML file
   :exception CloubedConfigurationException:
       * ``cloubed.yaml`` file could not be found or read in current directory
   :exception CloubedException:
       * the domain is not found in the YAML file
       * the template file is not found in the YAML file for this domain
       * the template input file could not be read or does not exist
       * the output file could not we written

.. py:function:: boot_vm(domain_name, bootdev = "hd", overwrite_disks = [], recreate_networks = [])

   Boot the domain `domain_name`. It also automatically checks that all its
   dependencies (networks, storage volumes and so on) already exist and create
   them if necessary.

   :param string domain_name: domain name in the YAML file
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

.. py:function:: wait_event(domain_name, event_type, event_detail)

   Waits for the event `type`:`detail` to happen on the domain `domain_name`.

   :param string domain_name: domain name in the YAML file
   :param string event_type: the type of the waited event
   :param string event_detail: the detail of the waited event

   :exception CloubedConfigurationException:
       * ``cloubed.yaml`` file could not be found or read in current directory
   :exception CloubedException:
       * the domain is not found in the YAML file
       * the event tuple type:detail is invalid
