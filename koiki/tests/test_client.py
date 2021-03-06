from unittest import TestCase
from unittest.mock import patch, MagicMock
import responses
import json

from koiki.client import Client
import koiki


class KoikiTest(TestCase):

    def setUp(self):
        self.order = {
            'order_key': 'xxx',
            'customer_note': 'delivery testing',
            'shipping': {
                'first_name': 'James',
                'last_name': 'Bond',
                'address_1': 'Address 1',
                'address_2': 'address 2',
                'postcode': '08025',
                'city': 'Barcelona',
                'state': 'Barcelona',
                'country': 'ES'
            },
            'billing': {
                'email': 'email@example.com',
                'phone': '+34666554433'
            },
            "line_items": [
                {
                    "id": 17,
                    "name": "Suc Taronja 1l",
                    "product_id": 5279,
                    "variation_id": 0,
                    "quantity": 1,
                    "meta_data": [
                        {
                            "id": 173,
                            "key": "_wcfmmp_order_item_processed",
                            "value": "5",
                            "display_key": "Store Order ID",
                            "display_value": "5"
                        },
                        {
                            "id": 172,
                            "key": "_vendor_id",
                            "value": "6",
                            "display_key": "Store",
                            "display_value": "Quèviure"
                        }
                    ],
                    "sku": "",
                    "price": 1,
                    "parent_name": None
                }
            ],
        }

        responses.add(responses.GET, f'{koiki.wcfmmp_host}/wp-json/wcfmmp/v1/settings/id/6',
                      status=200,
                      json={
                        "store_email": "queviure@lazona.coop",
                        "phone": "",
                        "address": {
                            "street_1": "",
                            "street_2": "",
                            "city": "",
                            "zip": "",
                            "country": "ES",
                            "state": ""
                        }
                      })

    @responses.activate
    @patch('koiki.logger', autospec=True)
    def test_create_delivery_successful_response(self, mock_logger):
        responses.add(responses.POST, 'https://testing_host/rekis/api/altaEnvios', status=200,
                      json={
                        'respuesta': '101',
                        'mensaje': 'OK',
                        'envios': [{'numPedido': '123', 'codBarras': 'yyy', 'etiqueta': 'abcd'}]
                      })

        delivery = Client(self.order).create_delivery()

        mock_logger.error.assert_not_called()
        self.assertEqual(delivery.to_dict(), {'number': '123', 'barcode': 'yyy', 'label': 'abcd'})

    @responses.activate
    @patch('koiki.logger', autospec=True)
    def test_create_delivery_failed_response(self, mock_logger):
        responses.add(responses.POST, 'https://testing_host/rekis/api/altaEnvios', status=400,
                      json={'error': 'Bad Request'})

        mock_logger = MagicMock()

        delivery = Client(self.order, logger=mock_logger).create_delivery()

        mock_logger.error.assert_called_once_with(
            'Koiki response. status=400, body={"error": "Bad Request"}')
        self.assertEqual(delivery.to_dict(), {'error': 'Bad Request'})

    @responses.activate
    def test_create_delivery_succesful_code_failed_response(self):
        responses.add(responses.POST, 'https://testing_host/rekis/api/altaEnvios', status=200,
                      json={'respuesta': '102', 'mensaje': 'TOKEN NOT FOUND', 'envios': []})

        mock_logger = MagicMock()

        delivery = Client(self.order, logger=mock_logger).create_delivery()

        mock_logger.error.assert_called_once_with(
            'Koiki response. status=200, body={"respuesta": "102", "mensaje": "TOKEN NOT FOUND", "envios": []}'  # noqa: E501
        )
        self.assertEqual(delivery.to_dict(), {'error': 'TOKEN NOT FOUND'})

    @responses.activate
    @patch('koiki.logger', autospec=True)
    @patch('koiki.client.requests.post', autospec=True)
    def test_create_delivery_sends_request(self, post_mock, _logger_mock):
        response = MagicMock()
        response.text = json.dumps(
            {
                'respuesta': '101',
                'mensaje': 'OK',
                'envios': [{'numPedido': '123', 'codBarras': 'yyy', 'etiqueta': 'abcd'}]
            }
        )
        response.status_code = 200
        post_mock.return_value = response

        Client(self.order, auth_token='xxx').create_delivery()

        post_mock.assert_called()
