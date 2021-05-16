from unittest import TestCase
from unittest.mock import patch, MagicMock
import urllib
import hashlib
import json
from sugarcrm.client import APIClient
from sugarcrm.error import CrmErrorAuthentication


class APIClientTest(TestCase):
    def setUp(self):
        self.mock_client = MagicMock()

    @patch("sugarcrm.logger", autospec=True)
    def test_success_login_request(self, mock_logger):
        http_mock_response = MagicMock()
        self.mock_client.urlopen = http_mock_response
        http_mock_response.return_value.read.return_value = json.dumps({"id": 111}).encode("utf-8")
        api_client = APIClient(self.mock_client, mock_logger)
        encode = hashlib.md5("test_sugarcrm_password".encode("utf-8"))
        encodedPassword = encode.hexdigest()
        data = json.dumps(
            {
                "user_auth": {
                    "user_name": "test_sugarcrm_user",
                    "password": encodedPassword,
                }
            }
        )
        args = {
            "method": "login",
            "input_type": "json",
            "response_type": "json",
            "rest_data": data,
        }

        params = urllib.parse.urlencode(args).encode("utf-8")
        http_mock_response.assert_called_once_with("https://test_sugarcrm_host", params)
        self.assertEqual(api_client.session_id, 111)
        self.assertEqual(mock_logger.debug.call_count, 2)

    def test_wrong_login_request(self):
        http_mock_response = MagicMock()
        self.mock_client.urlopen = http_mock_response
        http_mock_response.return_value.read.return_value = json.dumps({}).encode("utf-8")
        with self.assertRaises(CrmErrorAuthentication) as exception_context_manager:
            APIClient(self.mock_client)
        exception = exception_context_manager.exception
        self.assertEqual(exception.args, ("CRM Invalid Authentication",))
