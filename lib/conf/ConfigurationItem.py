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

from ..CloubedException import CloubedConfigurationException

class ConfigurationItem(object):

    """ Abstract ConfigurationItem class """

    def __init__(self, conf):

        self.name = None
        self.__parse_name(conf)

        # There is no real need for a dedicated __parse_testbed() method here
        # since this item is not a user input. It has been set in the conf
        # dictionary by the Configuration class which has already checked its
        # format and value previously.
        self.testbed = conf['testbed']

    def __parse_name(self, conf):
        """
            Parses the name parameter over the conf dictionary given in
            parameter and raises appropriate exception if a problem is found
        """

        if not conf.has_key('name'):
            raise CloubedConfigurationException(
                "one {type_name} object does not have a name" \
                    .format(type_name = self._get_type()))

        if type(conf['name']) is not str:
            raise CloubedConfigurationException(
                "the format of one {type_name} object is not valid" \
                    .format(type_name = self._get_type()))

        self.name = conf['name']

    def _get_type(self):

        """ Returns the type of the item """

        raise NotImplementedError

    @staticmethod
    def clean_string_for_template(string):

        return string.replace('-','')
