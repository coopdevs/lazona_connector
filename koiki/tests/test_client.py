from unittest import TestCase
from unittest.mock import patch, MagicMock
import responses
import json

from koiki.client import Client
import koiki


class KoikiTest(TestCase):

    def setUp(self):
        self.order = {
            'id': 33,
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

        responses.add(
                responses.GET,
                'https://wp_testing_host/wp-json/wp/v2/users/6?context=edit',
                status=200,
                content_type='application/json',
                json={
                    "id": 6,
                    "username": "Queviure",
                    "email": "queviure@lazona.coop",
                    "roles": ["testrole"],
                }
        )

    @responses.activate
    @patch('koiki.logger', autospec=True)
    def test_create_delivery_successful_response(self, mock_logger):
        responses.add(responses.POST, 'https://testing_host/rekis/api/altaEnvios', status=200,
                      json={
                        'respuesta': '101',
                        'mensaje': 'OK',
                        'envios': [{'numPedido': '123', 'codBarras': 'yyy', 'etiqueta': 'abcd'}]
                      })

        deliveries = Client(self.order).create_delivery()

        mock_logger.error.assert_not_called()
        self.assertEqual(deliveries[0].to_dict(), {'shipment_id': '123', 'barcode': 'yyy',
                                                   'label': 'abcd', 'order_id': 33,
                                                   'response': '', 'message': ''})

    @responses.activate
    @patch('koiki.logger', autospec=True)
    def test_create_delivery_failed_response(self, mock_logger):
        responses.add(responses.POST, 'https://testing_host/rekis/api/altaEnvios', status=400,
                      json={'error': 'Bad Request'})

        mock_logger = MagicMock()

        deliveries = Client(self.order, logger=mock_logger).create_delivery()

        mock_logger.error.assert_called_once_with(
            "Koiki response. status=400, body={'error': 'Bad Request'}")
        self.assertEqual(len(deliveries), 0)

    @responses.activate
    def test_create_delivery_succesful_code_failed_response(self):
        responses.add(responses.POST, 'https://testing_host/rekis/api/altaEnvios', status=200,
                      json={'respuesta': '102', 'mensaje': 'TOKEN NOT FOUND', 'envios': []})

        mock_logger = MagicMock()

        deliveries = Client(self.order, logger=mock_logger).create_delivery()

        self.assertEqual(len(deliveries), 0)

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
