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
import logging

def gen_mac(salt):

    """
       Simple utility/function to generate a MAC address with the salt given in
       parameter
    """

    salted = hashlib.sha1(salt).hexdigest()[:6]
    mac = [ "00", "16", "3e" ]
    mac.extend((salted[:2], salted[2:4], salted[4:6]))
    return ':'.join(mac)

def net_conflict(ip1, mask1, ip2, mask2):
    """Returns true is the two IPv4 networks are in conflict.
       If the netaddr module is not available, a debug message is printed and
       False is returned.
       If the format of one the parameter is not valid (could not lead to a
       valid IPv4 IP set), a debug message is printed and False is returned.

       :param string ip1: IP address of network 1
       :param string mask1: netmask of network 1
       :param string ip2: IP address of network 2
       :param string mask2: netmask of network 2
    """

    try:
        from netaddr import IPSet, AddrFormatError
    except ImportError:
        logging.debug("unable to check conflicting networks since netaddr " \
                      "module is not available")
        return False

    try:
        set1 = IPSet(['{ip}/{mask}'.format(ip=ip1, mask=mask1)])
        set2 = IPSet(['{ip}/{mask}'.format(ip=ip2, mask=mask2)])
    except AddrFormatError, err:
        logging.debug("unable to check conflicting networks due to error in " \
                      "address format: {error}".format(error=err))
        return False

    return not set1.isdisjoint(set2)

def getuser():

    """
       Return the username of the current user
    """
    # why not os.getlogin()? see details in python issue #584566
    # http://bugs.python.org/issue584566
    return pwd.getpwuid(os.geteuid())[0]
