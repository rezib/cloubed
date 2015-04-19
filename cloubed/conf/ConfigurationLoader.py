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

""" ConfigurationLoader class """

import yaml
from cloubed.CloubedException import CloubedConfigurationException

class ConfigurationLoader:

    """ ConfigurationLoader class """

    def __init__(self, conf_file):

        self.file_path = conf_file

        try:
            yaml_file = open(self.file_path)
        except IOError:
            raise CloubedConfigurationException(
                      "Not able to open file {file_path}" \
                          .format(file_path = self.file_path))

        try:
            self.content = yaml.load(yaml_file)
        except yaml.YAMLError as err:
            raise CloubedConfigurationException(
                      "Error while loading {file_path} file (may" \
                      " not be valid YAML content): {error}" \
                          .format(file_path=self.file_path,
                                  error=err))
        yaml_file.close()

        if type(self.content) is not dict:
            raise CloubedConfigurationException(
                      "File {file_path} is not a valid YAML file for Cloubed" \
                          .format(file_path=self.file_path))
