from unittest import TestCase
from unittest.mock import patch, MagicMock
import hashlib
import json
from sugarcrm.client import APIClient
from sugarcrm.error import CrmAuthenticationError


class APIClientTest(TestCase):
    def setUp(self):
        self.mock_client = MagicMock()

    @patch("sugarcrm.logger", autospec=True)
    def test_success_login_request(self, mock_logger):
        http_mock_response = MagicMock()
        self.mock_client.get = http_mock_response
        http_mock_response.return_value.json.return_value = {"id": 111}
        api_client = APIClient(self.mock_client, mock_logger)
        api_client.login()

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

        http_mock_response.assert_called_once_with("https://test_sugarcrm_host", args)
        self.assertEqual(api_client.session_id, 111)
        self.assertEqual(mock_logger.debug.call_count, 2)

    def test_wrong_login_request(self):
        http_mock_response = MagicMock()
        self.mock_client.get = http_mock_response
        http_mock_response.return_value.json.return_value = {}
        with self.assertRaises(CrmAuthenticationError) as exception_context_manager:
            APIClient(self.mock_client).login()
        exception = exception_context_manager.exception
        self.assertEqual(exception.args, ("CRM Invalid Authentication",))