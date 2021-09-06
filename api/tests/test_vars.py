import os
import importlib

from unittest.mock import patch
from django.test import TestCase
import lazona_connector.vars


class EnvVarsTests(TestCase):

    @patch("sys.argv", autospec=True)
    def test_create_shipment_successful(self, mock_vars):
        mock_vars.return_value = []
        importlib.reload(lazona_connector.vars)
        self.assertEqual(lazona_connector.vars.sugarcrm_password, os.getenv('SUGARCRM_PASSWORD'))
        self.assertNotEqual(lazona_connector.vars.sugarcrm_password, "test_sugarcrm_password")

    def tearDown(self):
        importlib.reload(lazona_connector.vars)
