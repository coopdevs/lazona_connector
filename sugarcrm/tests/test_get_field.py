from unittest import TestCase
from unittest.mock import MagicMock
from sugarcrm.client import APIClient
from sugarcrm.error import CrmResponseError


class GetFieldTest(TestCase):
    def setUp(self):
        self.mock_client = MagicMock()
        self.object_id = "CONTACT_RECORD_ID"
        self.field_to_get = "myfield"
        self.value_to_get = "FIELD_VALUE_ID"

    def test_success_get_field_request(self):
        http_mock_response = MagicMock()
        self.mock_client.get = http_mock_response
        api_client = APIClient(self.mock_client)
        api_client.session_id = 1
        http_mock_response.return_value.json.return_value = {
                "entry_list": [
                    {
                        "name_value_list": {self.field_to_get: {"value": self.value_to_get}},
                    }
                ]
        }
        value = api_client.get_field("Module", self.object_id, self.field_to_get)

        self.assertEqual(self.value_to_get, value)

    def test_wrong_get_field_request(self):
        http_mock_response = MagicMock()
        self.mock_client.get = http_mock_response
        api_client = APIClient(self.mock_client)
        api_client.session_id = 1

        http_mock_response.return_value.json.return_value = {}
        with self.assertRaises(CrmResponseError):
            _ = api_client.get_field("Module", self.object_id, self.field_to_get)
