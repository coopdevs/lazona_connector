from unittest import TestCase
from unittest.mock import patch, MagicMock

from koiki.woocommerce.wcfmmp import APIClient


class APIClientTest(TestCase):

    def setUp(self):
        self.mock_client = MagicMock()

    def test_request(self):
        self.mock_client.get = MagicMock()

        api_client = APIClient(self.mock_client)
        api_client.request('endpoint')

        self.mock_client.get.assert_called_once_with(
                'http://staging.lazona.coop/wp-json/wcfmmp/v1/settings/endpoint')

    @patch('koiki.woocommerce.wcfmmp.logging', autospec=True)
    def test_request_logging(self, mock_logger):
        api_client = APIClient(self.mock_client, mock_logger)
        api_client.request('endpoint')

        mock_logger.info.assert_called_once_with(
            'Wcfmpp request. url=http://staging.lazona.coop/wp-json/wcfmmp/v1/settings/endpoint')
