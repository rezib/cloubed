#!/usr/bin/env python

import os

from CloubedTests import *

from lib.conf.ConfigurationLoader import ConfigurationLoader
from lib.CloubedException import CloubedConfigurationException

class TestConfigurationLoader(CloubedTestCase):

    def setUp(self):
        filename = "cloubed_valid.yaml"
        self.abs_filename = os.path.join(os.getcwd(), "config", filename)
        self.configuration_loader = ConfigurationLoader(self.abs_filename)

    def test_attr_file_path(self):
        """
            ConfigurationLoader.file_path should be the absolute path to the
            YAML file
        """

        self.assertEquals(self.configuration_loader.file_path,
                          self.abs_filename)

    def test_attr_content(self):
        """
            ConfigurationLoader.content should be a dict with the content of the
            YAML file
        """
        self.assertEquals(self.configuration_loader.content,
                          { 'yaml': 'cloubed' })

class TestConfigurationLoaderInvalid(CloubedTestCase):

    def setUp(self):
        pass

    def test_nonexisting_yaml(self):
        """
            ConfigurationLoader init should raise CloubedConfigurationException
            if YAML file does not exist
        """
        filename = "cloubed_nonexisting_file.yaml"
        abs_filename = os.path.join(os.getcwd(), "config", filename)
        self.assertRaisesRegexp(CloubedConfigurationException,
                                "Not able to open file .*/config/{0}" \
                                    .format(filename),
                                ConfigurationLoader,
                                abs_filename)



    def test_empty_yaml(self):
        """
            ConfigurationLoader init should raise CloubedConfigurationException
            if YAML file is empty
        """
        filename = "cloubed_empty.yaml"
        abs_filename = os.path.join(os.getcwd(), "config", filename)
        self.assertRaisesRegexp(CloubedConfigurationException,
                                "File .*/config/{0} is not a valid YAML file " \
                                "for Cloubed" \
                                    .format(filename),
                                ConfigurationLoader,
                                abs_filename)

    def test_invalid_content(self):
        """
            ConfigurationLoader init should raise CloubedConfigurationException
            if YAML file is not valid
        """
        filename = "cloubed_invalid_yaml.txt"
        abs_filename = os.path.join(os.getcwd(), "config", filename)
        self.assertRaisesRegexp(CloubedConfigurationException,
                                "File .*/config/{0} is not a valid YAML file " \
                                "for Cloubed" \
                                    .format(filename),
                                ConfigurationLoader,
                                abs_filename)

    def test_invalid_yaml(self):
        """
            ConfigurationLoader init should raise CloubedConfigurationException
            if YAML file is not valid
        """
        filename = "yaml.png"
        abs_filename = os.path.join(os.getcwd(), "config", filename)
        self.assertRaisesRegexp(CloubedConfigurationException,
                                "Error while loading .*/config/{0} file \(may " \
                                "not be valid YAML content\):" \
                                    .format(filename),
                                ConfigurationLoader,
                                abs_filename)

loadtestcase(TestConfigurationLoader)
loadtestcase(TestConfigurationLoaderInvalid)
