#!/usr/bin/python3
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

""" EventManager class of Cloubed """

import threading
import logging

from cloubed.VirtController import VirtController
from cloubed.DomainEvent import DomainEvent

class EventManager:

    """ EventManager class """

    tbd = None

    def __init__(self, tbd):

        VirtController.event_register()
        self._stop = threading.Event()

        self._thread = threading.Thread(target=self.run_event_loop,
                                        name="libvirtEventLoop")
        self._thread.setDaemon(True)
        self._thread.start()

        self._ctl = VirtController(read_only=True)
        self._ctl.domain_event_register(EventManager.manage_event)
        self._ctl.setKeepAlive(5, 3)

        EventManager.tbd = tbd

        logging.debug("initialized event manager")

    def terminate(self):

        logging.debug("terminating event manager thread")
        self._stop.set()

    def run_event_loop(self):

        """ run_event_loop: Starts libvirt event loop """

        # In race conditions on python interpreter exit, libvirt sometimes
        # becomes None. So loop conditioner tests if it is still defined in
        # order to avoid  errors.
        while not self._stop.is_set():
            VirtController.event_run()

    @staticmethod
    def manage_event(conn, dom, event_type, event_detail, opaque):

        """ manage_event: handler launched by libvirt in case of event """

        event = DomainEvent(event_type, event_detail)
        logging.debug("event on domain {domain_name}({domain_id}) " \
                      "{event_type} {event_detail}" \
                          .format(domain_name=dom.name(),
                                  domain_id=dom.ID(),
                                  event_type=event.type,
                                  event_detail=event.detail))

        domain = EventManager.tbd.get_domain_by_libvirt_name(dom.name())
        # test if notified event comes from a domain in current testbed
        if domain is None:
            logging.debug("event received for domain {domain} but not found " \
                          "in testbed".format(domain=dom.name()))
        else:
            domain.notify_event(event)

