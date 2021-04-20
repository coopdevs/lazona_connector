from unittest import TestCase
from unittest.mock import patch, MagicMock
import responses
import json

from koiki.client import Client


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
                    "tax_class": "",
                    "subtotal": "1.00",
                    "subtotal_tax": "0.00",
                    "total": "1.00",
                    "total_tax": "0.00",
                    "taxes": [],
                    "meta_data": [
                        {
                            "id": 172,
                            "key": "_vendor_id",
                            "value": "6",
                            "display_key": "Store",
                            "display_value": "Quèviure"
                            },
                        {
                            "id": 173,
                            "key": "_wcfmmp_order_item_processed",
                            "value": "5",
                            "display_key": "Store Order ID",
                            "display_value": "5"
                            }
                    ],
                    "sku": "",
                    "price": 1,
                    "parent_name": None
                }
            ],
        }

    @responses.activate
    @patch('koiki.client.logging', autospec=True)
    def test_create_delivery_successful_response(self, mock_logger):
        responses.add(responses.POST, 'https://testing_host/rekis/api/altaEnvios',
                      json={
                        'respuesta': '101',
                        'mensaje': 'OK',
                        'envios': [{'numPedido': '123', 'codBarras': 'yyy', 'etiqueta': 'abcd'}]
                      },
                      status=200)

        delivery = Client(self.order).create_delivery()

        mock_logger.error.assert_not_called()
        self.assertEqual(delivery.to_dict(), {'number': '123', 'barcode': 'yyy', 'label': 'abcd'})

    @responses.activate
    @patch('koiki.client.logging', autospec=True)
    def test_create_delivery_failed_response(self, mock_logger):
        responses.add(responses.POST, 'https://testing_host/rekis/api/altaEnvios',
                      json={'error': 'Bad Request'}, status=400)
        mock_logger = MagicMock()

        delivery = Client(self.order, logger=mock_logger).create_delivery()

        mock_logger.error.assert_called_once_with(
            'Koiki response. status=400, body={"error": "Bad Request"}')
        self.assertEqual(delivery.to_dict(), {'error': 'Bad Request'})

    @responses.activate
    def test_create_delivery_succesful_code_failed_response(self):
        responses.add(responses.POST, 'https://testing_host/rekis/api/altaEnvios',
                      json={'respuesta': '102', 'mensaje': 'TOKEN NOT FOUND', 'envios': []},
                      status=200)
        mock_logger = MagicMock()

        delivery = Client(self.order, logger=mock_logger).create_delivery()

        mock_logger.error.assert_called_once_with(
            'Koiki response. status=200, body={"respuesta": "102", "mensaje": "TOKEN NOT FOUND", "envios": []}'  # noqa: E501
        )
        self.assertEqual(delivery.to_dict(), {'error': 'TOKEN NOT FOUND'})

    @patch('koiki.client.logging', autospec=True)
    @patch('koiki.client.requests.post', autospec=True)
    def test_create_delivery_sends_request_with_body(self, post_mock, _logger_mock):
        shipping = self.order['shipping']
        billing = self.order['billing']

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

        post_mock.assert_called_with(
            'https://testing_host/rekis/api/altaEnvios',
            json={
                'token': 'xxx',
                'formatoEtiqueta': 'PDF',
                'envios': [
                    {
                        'numPedido': self.order['order_key'],
                        'bultos': 1,
                        'kilos': 1.0,
                        'tipoServicio': '',
                        'reembolso': 0.0,
                        'observaciones': self.order['customer_note'],

                        'nombreRemi': 'La Zona',
                        'apellidoRemi': '',
                        'direccionRemi': 'C/ La Zona, 1',
                        'numeroCalleRemi': '',
                        'codPostalRemi': '08186',
                        'poblacionRemi': 'Barcelona',
                        'provinciaRemi': 'Barcelona',
                        'paisRemi': 'ES',
                        'emailRemi': 'lazona@opcions.org',
                        'telefonoRemi': '518888191',

                        'nombreDesti': shipping['first_name'],
                        'apellidoDesti': shipping['last_name'],
                        'direccionDesti': shipping['address_1'],
                        'direccionAdicionalDesti': shipping['address_2'],
                        'numeroCalleDesti': '',
                        'codPostalDesti': shipping['postcode'],
                        'poblacionDesti': shipping['city'],
                        'provinciaDesti': shipping['state'],
                        'paisDesti': shipping['country'],

                        'telefonoDesti': billing['phone'],
                        'emailDesti': billing['email'],
                    }
                ]
            }
        )
