from unittest import TestCase
from unittest.mock import patch, MagicMock
from wordpress.client import APIClient


class APIClientTest(TestCase):
    def setUp(self):
        self.mock_client = MagicMock()

    def test_request(self):
        self.mock_client.get = MagicMock()

        api_client = APIClient(self.mock_client)
        api_client.get_request('endpoint')

        self.mock_client.get.assert_called_once_with(
            'https://test_wp_host/wp-json/wp/v2/endpoint', params={},
            auth=('test_wp_user', 'test_wp_password')
        )

    @patch('wordpress.logger', autospec=True)
    def test_request_logging(self, mock_logger):
        api_client = APIClient(self.mock_client, mock_logger)
        api_client.get_request('endpoint')

        mock_logger.info.assert_called_once_with(
            'WP GET request. url=https://test_wp_host/wp-json/wp/v2/endpoint. params={}')

    def test_failed_request(self):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        self.mock_client.get.return_value = mock_response

        api_client = APIClient(self.mock_client)
        api_client.get_request('endpoint')

        mock_response.raise_for_status.assert_called_once()
