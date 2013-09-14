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

""" Exceptions classes of Cloubed"""

class CloubedException(Exception):

    """ Base class for exceptions in Cloubed """

    def __init__(self, msg):

        super(CloubedException, self).__init__(msg)
        self.msg = msg

    def __str__(self):

        return "{msg}".format(msg=self.msg)

class CloubedArgumentException(CloubedException):

    """ Class for CLI arguments exceptions in Cloubed """

    def __init__(self, msg):

        super(CloubedArgumentException, self).__init__(msg)
