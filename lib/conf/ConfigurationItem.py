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

""" ConfigurationItem class """

class ConfigurationItem(object):

    """ Abstract ConfigurationItem class """

    def __init__(self, conf):

        self._name = conf['name']
        self._testbed = conf['testbed']

    def get_name(self):

        """ Returns the name of the item """

        return self._name

    def get_testbed(self):

        """ Returns the name of the testbed """

        return self._testbed

    @staticmethod
    def clean_string_for_template(string):

        return string.replace('-','')
