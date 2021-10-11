from unittest import TestCase
from unittest.mock import patch, MagicMock
from wordpress.client import APIClient


class APIClientTest(TestCase):
    def setUp(self):
        self.mock_client = MagicMock()

    @patch("lazona_connector.vars.logger", autospec=True)
    def test_get_request(self, mock_logger):
        self.mock_client.get = MagicMock()

        api_client = APIClient(self.mock_client, mock_logger)
        api_client.get_request("endpoint")

        mock_logger.info.assert_called_once_with(
            "WP GET request. url=https://wcfmmp_testing_host/wp-json/wp/v2/endpoint. params={}"
        )

        self.mock_client.get.assert_called_once_with(
            "https://wcfmmp_testing_host/wp-json/wp/v2/endpoint",
            params={},
            auth=("test_wcfmmp_user", "test_wcfmmp_password"),
        )

    @patch("lazona_connector.vars.logger", autospec=True)
    def test_post_request(self, mock_logger):
        api_client = APIClient(self.mock_client, mock_logger)
        test_data = {"field": "data"}
        api_client.post_request("endpoint", test_data)

        mock_logger.info.assert_called_once_with(
            "WP POST request. url=https://wcfmmp_testing_host/wp-json/wp/v2/endpoint."
            " data={'field': 'data'}"
        )

        self.mock_client.post.assert_called_once_with(
            "https://wcfmmp_testing_host/wp-json/wp/v2/endpoint",
            data=test_data,
            auth=("test_wcfmmp_user", "test_wcfmmp_password"),
        )

    def test_failed_request(self):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        self.mock_client.get.return_value = mock_response

        api_client = APIClient(self.mock_client)
        api_client.get_request("endpoint")

        mock_response.raise_for_status.assert_called_once()
