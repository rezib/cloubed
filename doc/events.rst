Events reference
================

The following tables lists all possible combinations of event types and details
that may happen on a domain managed by Libvirt:

+-----------------+-------------------+--------------------------------------+
| type            | detail            | description                          |
+=================+===================+======================================+
| ``defined``     | ``added``         | newly created config file            |
|                 +-------------------+--------------------------------------+
|                 | ``updated``       | changed config file                  |
+-----------------+-------------------+--------------------------------------+
| ``undefined``   | ``removed``       | deleted the config file              |
+-----------------+-------------------+--------------------------------------+
| ``started``     | ``booted``        | normal startup from boot             |
|                 +-------------------+--------------------------------------+
|                 | ``migrated``      | incoming migration from another host |
|                 +-------------------+--------------------------------------+
|                 | ``restored``      | suspended due to a disk I/O error    |
|                 +-------------------+--------------------------------------+
|                 | ``from_snapshot`` | restored from snapshot               |
|                 +-------------------+--------------------------------------+
|                 | ``wakeup``        | started due to wakeup event          |
+-----------------+-------------------+--------------------------------------+
| ``suspended``   | ``paused``        | normal suspend due to admin pause    |
|                 +-------------------+--------------------------------------+
|                 | ``migrated``      | suspended for offline migration      |
|                 +-------------------+--------------------------------------+
|                 | ``ioerror``       | suspended due to a disk I/O error    |
|                 +-------------------+--------------------------------------+
|                 | ``watchdog``      | suspended due to a watchdog firing   |
|                 +-------------------+--------------------------------------+
|                 | ``restored``      | restored from paused state file      |
|                 +-------------------+--------------------------------------+
|                 | ``from_snapshot`` | restored from paused snapshot        |
|                 +-------------------+--------------------------------------+
|                 | ``api_error``     | suspended after failure during       |
|                 |                   | libvirt API call                     |
+-----------------+-------------------+--------------------------------------+
| ``resumed``     | ``unpaused``      | normal resume due to admin unpause   |
|                 +-------------------+--------------------------------------+
|                 | ``migrated``      | resumed for completion during        |
|                 |                   | migration                            |
|                 +-------------------+--------------------------------------+
|                 | ``from_snapshot`` | resumed from snapshot                |
+-----------------+-------------------+--------------------------------------+
| ``stopped``     | ``shutdown``      | normal shutdown                      |
|                 +-------------------+--------------------------------------+
|                 | ``destroyed``     | forced poweroff from host            |
|                 +-------------------+--------------------------------------+
|                 | ``crashed``       | guest crashed                        |
|                 +-------------------+--------------------------------------+
|                 | ``migrated``      | migrated off to another host         |
|                 +-------------------+--------------------------------------+
|                 | ``saved``         | saved to a state file                |
|                 +-------------------+--------------------------------------+
|                 | ``failed``        | host emulator/mgmt failed            |
|                 +-------------------+--------------------------------------+
|                 | ``from_snapshot`` | offline snapshot loaded              |
+-----------------+-------------------+--------------------------------------+
| ``shutdown``    | ``finished``      | guest finished shutdown sequence     |
+-----------------+-------------------+--------------------------------------+
| ``pmsuspended`` | ``memory``        | guest was PM suspended to memory     |
|                 +-------------------+--------------------------------------+
|                 | ``disk``          | guest was PM suspended to disk       |
+-----------------+-------------------+--------------------------------------+
