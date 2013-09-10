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

""" HTTPServer class of Cloubed """

import SimpleHTTPServer
import SocketServer
import threading

class HTTPServer():

    """ HTTPServer class """

    def __init__(self, address):

        self._port = 5432
        self._handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        self._address = address
        self._httpd = None
        self._thread = None

    def launched(self):

        """
           Returns True if the HTTPServer is already launched
        """

        return self._thread is not None

    def launch(self):

        """
            launch: Creates the daemon thread that will start the HTTP server
        """

        self._thread = threading.Thread(target=self.threaded_server,
                                        name="ClouBedHTTPServer")
        self._thread.setDaemon(True)
        self._thread.start()

    def threaded_server(self):

        """
            threaded_server: Thread routine that actually starts the HTTP server
        """

        self._httpd = SocketServer.TCPServer((self._address, self._port),
                                             self._handler)
        self._httpd.serve_forever()

