#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Rémi Palancher 
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

""" Set of utilities functions for Cloubed """

import hashlib
import pwd
import os

def gen_mac(salt):

    """
       Simple utility/function to generate a MAC address with the salt given in
       parameter
    """

    salted = hashlib.sha1(salt).hexdigest()[:6]
    mac = [ "00", "16", "3e" ]
    mac.extend((salted[:2], salted[2:4], salted[4:6]))
    return ':'.join(mac)

def getuser():

    """
       Return the username of the current user
    """
    # why not os.getlogin()? see details in python issue #584566
    # http://bugs.python.org/issue584566
    return pwd.getpwuid(os.geteuid())[0]
