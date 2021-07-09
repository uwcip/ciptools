import os
from unittest import TestCase, mock

import ciptools.configuration


class ConfigurationTests(TestCase):
    def test_load_conf1(self):
        environment, configuration = ciptools.configuration.load_configuration(package="tests.configurations", environment="test1")
        self.assertEqual(environment, "test1")
        self.assertEqual(configuration, {"FOO": "bar"})

    @mock.patch.dict(os.environ, {"ENVIRONMENT": "test2"})
    def test_load_conf2(self):
        environment, configuration = ciptools.configuration.load_configuration(package="tests.configurations")
        self.assertEqual(environment, "test2")
        self.assertEqual(configuration, {"BAZ": "bat"})

    @mock.patch.dict(os.environ, {"ENVIRONMENT": "test3"})
    def test_load_conf3(self):
        environment, configuration = ciptools.configuration.load_configuration()
        self.assertEqual(environment, "test3")
        self.assertEqual(configuration, {"FIZZ": "buzz"})
