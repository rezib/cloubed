#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013 Rémi Palancher 
#
# This file is part of Cloubed.
#
# Cloubed is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# Cloubed is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with Cloubed.  If not, see
# <http://www.gnu.org/licenses/>.

""" DomainEvent class of Cloubed """

import logging

class DomainEvent:

    """ DomainEvent class """

    _domain_event_infos = {
        0: ["DEFINED",     {
            0: "DEFINED_ADDED", # newly created config file
            1: "DEFINED_UPDATED", # changed config file
            2: "DEFINED_LAST" }
           ],
        1: ["UNDEFINED",   {
            0: "UNDEFINED_REMOVED", # deleted the config file
            1: "UNDEFINED_LAST" }
           ],
        2: ["STARTED",     {
            0: "STARTED_BOOTED", # normal startup from boot
            1: "STARTED_MIGRATED", # incoming migration from another host
            2: "STARTED_RESTORED", # restored from a state file
            3: "STARTED_FROM_SNAPSHOT", # restored from snapshot
            4: "STARTED_WAKEUP", # started due to wakeup event
            5: "STARTED_LAST" }
           ],
        3: ["SUSPENDED",   {
            0: "SUSPENDED_PAUSED", # normal suspend due to admin pause
            1: "SUSPENDED_MIGRATED", # suspended for offline migration
            2: "SUSPENDED_IOERROR", # suspended due to a disk I/O error
            3: "SUSPENDED_WATCHDOG", # suspended due to a watchdog firing
            4: "SUSPENDED_RESTORED", # restored from paused state file
            5: "SUSPENDED_FROM_SNAPSHOT", # restored from paused snapshot
            6: "SUSPENDED_API_ERROR", # suspended after failure during libvirt
                                      # API call
            7: "SUSPENDED_LAST" }
           ],
        4: ["RESUMED",     {
            0: "RESUMED_UNPAUSED", # normal resume due to admin unpause
            1: "RESUMED_MIGRATED", # resumed for completion during migration
            2: "RESUMED_FROM_SNAPSHOT", # resumed from snapshot
            3: "RESUMED_LAST" }
           ],
        5: ["STOPPED",     {
            0: "STOPPED_SHUTDOWN", # normal shutdown
            1: "STOPPED_DESTROYED", # forced poweroff from host
            2: "STOPPED_CRASHED", # guest crashed
            3: "STOPPED_MIGRATED", # migrated off to another host
            4: "STOPPED_SAVED", # saved to a state file
            5: "STOPPED_FAILED", # host emulator/mgmt failed
            6: "STOPPED_FROM_SNAPSHOT", # offline snapshot loaded
            7: "STOPPED_LAST" }
           ],
        6: ["SHUTDOWN",    {
            0: "SHUTDOWN_FINISHED", # guest finished shutdown sequence
            1: "SHUTDOWN_LAST" }
           ],
        7: ["PMSUSPENDED", {
            0: "PMSUSPENDED_MEMORY", # guest was PM suspended to memory
            1: "PMSUSPENDED_DISK", # guest was PM suspended tp disk
            2: "PMSUSPENDED_LAST" }
           ],
        8: ["LAST", None ]
    }

    def __init__(self, event_type, event_detail):

        if isinstance(event_type, int) and isinstance(event_detail, int):

            self._type = DomainEvent \
                             ._domain_event_infos[event_type][0]
            self._detail = DomainEvent \
                               ._domain_event_infos[event_type][1][event_detail]

        elif isinstance(event_type, str) and isinstance(event_detail, str):

            self._type = event_type
            self._detail = event_detail

        else:

            return None

    def __str__(self):

        return "{event_type}>{event_detail}" \
                   .format(event_type=self._type, event_detail=self._detail)

    def __eq__(self, other):

        logging.debug("comparing events: {event1} {event2}" \
                          .format(event1=self, event2=other))

        if self._type == other.get_type() \
           and self._detail == other.get_detail():
            return True

        return False

    def get_type(self):

        """ get_type: Returns the type of the DomainEvent """

        return self._type

    def get_detail(self):

        """ get_detail: """

        return self._detail

    @classmethod
    def get_event_info(cls, event_type, event_detail):

        """
            get_event_info: Returns both the type name and the detail of the
            DomainEvent
        """

        return (cls._domain_event_infos[event_type][0],
                cls._domain_event_infos[event_type][1][event_detail])
