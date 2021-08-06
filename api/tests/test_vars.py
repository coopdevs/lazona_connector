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
        self.assertEqual(lazona_connector.vars.koiki_host, os.getenv('SUGARCRM_PASSWORD'))
        self.assertNotEqual(lazona_connector.vars.koiki_host, "test_sugarcrm_password")
