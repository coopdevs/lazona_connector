from unittest import TestCase
from unittest.mock import patch
import responses

from koiki import Client

class KoikiTest(TestCase):

    def setUp(self):
        self.order = {
            'order_key': 'xxx',
            'shipping': {
                'first_name': 'James',
                'last_name': 'Bond',
                'address_1': 'Address 1',
                'address_2': 'address 2',
                'postcode': '08025',
                'city': 'Barcelona',
                'state': 'Barcelona',
                'country': 'Spain'
            },
            'billing': {
                'email': 'email@example.com',
                'phone': '+34666554433'
            }
        }

    @responses.activate
    @patch('koiki.client.logging', autospec=True)
    def test_create_delivery_successful_response(self, mock_logger):
        responses.add(responses.POST, 'https://rekistest.koiki.es/services/rekis/api/altaEnvios',
                  json={}, status=200)

        self.assertTrue(Client(self.order).create_delivery())
        mock_logger.error.assert_not_called()

    @responses.activate
    @patch('koiki.client.logging', autospec=True)
    def test_create_delivery_failed_response(self, mock_logger):
        responses.add(responses.POST, 'https://rekistest.koiki.es/services/rekis/api/altaEnvios',
                  json={'error': 'Bad Request'}, status=400)

        self.assertFalse(Client(self.order).create_delivery())
        mock_logger.error.assert_called_once_with(
            'Failed request. status=%s, body=%s',
            400,
            '{"error": "Bad Request"}'
        )

    @patch('koiki.client.requests.post', autospec=True)
    def test_create_delivery_sends_request_with_body(self, post_mock):
        """create_delivery builds the delivery based on the specified order"""
        shipping = self.order['shipping']
        billing = self.order['billing']

        Client(self.order).create_delivery()

        post_mock.assert_called_with(
            'https://rekistest.koiki.es/services/rekis/api/altaEnvios',
            json={
                'formatoEtiqueta': 'PDF',
                'envios': [
                    {
                        'numPedido': self.order['order_key'],

                        'nombreRemi': 'La Zona',
                        'direccionRemi': 'C/ La Zona, 1',
                        'codPostalRemi': '08186',
                        'poblacionRemi': 'Barcelona',
                        'provinciaRemi': 'Barcelona',
                        'paisRemi': 'ES',
                        'emailRemi': 'lazona@opcions.org',
                        'telefonoRemi': '+34518888191',

                        'nombreDesti': shipping['first_name'],
                        'apellidoDesti': shipping['last_name'],
                        'direccionDesti': shipping['address_1'] + shipping['address_2'],
                        'codPostalDesti': shipping['postcode'],
                        'poblacionDesti': shipping['city'],
                        'provinciaDesti': shipping['state'],
                        'paisDesti': shipping['country'],

                        'telefonoDesti': billing['phone'],
                        'emailDesti': billing['email']
                    }
                ]
            }
        )

    @patch('koiki.client.Sender')
    def test_create_delivery_calls_sender(self, MockSender):
        Client(self.order).create_delivery()
        MockSender().to_dict.assert_called_once()

    @patch('koiki.client.Recipient')
    def test_create_delivery_calls_sender(self, MockRecipient):
        Client(self.order).create_delivery()
        MockRecipient().to_dict.assert_called_once()
