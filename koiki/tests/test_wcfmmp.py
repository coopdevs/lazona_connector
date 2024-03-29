from unittest import TestCase
from unittest.mock import patch, MagicMock
import lazona_connector.vars
from koiki.woocommerce.wcfmmp import APIClient


class APIClientTest(TestCase):
    def setUp(self):
        self.mock_client = MagicMock()

    def test_request(self):
        self.mock_client.get = MagicMock()

        api_client = APIClient(self.mock_client)
        api_client.request("endpoint")

        self.mock_client.get.assert_called_once_with(
            f"{lazona_connector.vars.wcfmmp_host}/wp-json/wcfmmp/v1/endpoint",
            auth=(lazona_connector.vars.wcfmmp_user, lazona_connector.vars.wcfmmp_password),
        )

    @patch("lazona_connector.vars.logger", autospec=True)
    def test_request_logging(self, mock_logger):
        api_client = APIClient(self.mock_client, mock_logger)
        api_client.request("endpoint")

        mock_logger.info.assert_called_once_with(
            f"Wcfmpp request. url={lazona_connector.vars.wcfmmp_host}/wp-json/wcfmmp/v1/endpoint"
        )

    def test_failed_request(self):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        self.mock_client.get.return_value = mock_response

        api_client = APIClient(self.mock_client)
        api_client.request("endpoint")

        mock_response.raise_for_status.assert_called_once()
