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

""" DomainTemplate class of Cloubed """

from string import Template
from CloubedException import CloubedException

class ExtTemplate(Template):

    """
        ExtTemplate class: child of standard Template in order to change the
                           pattern of allowed set of characters
    """

    # add '.' to the list of allowed characters
    idpattern = r'[a-z][_a-z0-9]*(\.[a-z][_a-z0-9]*)*'

class DomainTemplate():

    """ DomainTemplate class """

    _dict = None

    def __init__(self, domain_template_conf):

        self._name = domain_template_conf['name']
        self._source_file = domain_template_conf['input']
        self._output_file = domain_template_conf['output']

    def get_name(self):

        """ get_name: Returns the name of the template """

        return self._name

    def render(self, template_dict):

        """ render: renders the template """

        template_str = ExtTemplate(open(self._source_file, 'r').read()) \
                           .safe_substitute(template_dict)
        try:
            output_file = open(self._output_file, 'w')
            output_file.write(template_str)
            output_file.close()
        except IOError, err:
            raise CloubedException(
                      "error while writing to template file {filename}: {err}" \
                          .format(filename = self._output_file,
                                  err = err))
