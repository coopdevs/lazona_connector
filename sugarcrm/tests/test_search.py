from unittest import TestCase
from unittest.mock import patch, MagicMock, call
import json
from sugarcrm.client import APIClient
from sugarcrm.error import CrmResponseError


class SearchTest(TestCase):
    def setUp(self):
        self.mock_client = MagicMock()
        self.email = "test@test.com"

    @patch("sugarcrm.logger", autospec=True)
    def test_success_search_request(self, mock_logger):
        http_mock_response = MagicMock()
        self.mock_client.get = http_mock_response
        api_client = APIClient(self.mock_client, mock_logger)
        http_mock_response.return_value.json.return_value = {
                "entry_list": [
                    {"name": "Accounts", "records": []},
                    {
                        "name": "Contacts",
                        "records": [{"id": {"name": "id", "value": "CONTACT_RECORD_ID"}}],
                    },
                ]
        }

        account_id, contact_id = api_client.search_email(self.email)
        mock_logger.info.assert_has_calls(
            [
                call("SugarCRM searching email: {}".format(self.email)),
                call("Found account_id: None, contact_id: CONTACT_RECORD_ID"),
            ]
        )

        self.assertEqual(contact_id, "CONTACT_RECORD_ID")
        self.assertIsNone(account_id)

    def test_wrong_search_request(self):
        http_mock_response = MagicMock()
        self.mock_client.get = http_mock_response
        api_client = APIClient(self.mock_client)

        http_mock_response.return_value.json.return_value = {}
        with self.assertRaises(CrmResponseError):
            _, _ = api_client.search_email(self.email)
