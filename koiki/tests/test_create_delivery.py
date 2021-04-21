from unittest import TestCase
from unittest.mock import patch, MagicMock

from koiki.create_delivery import CreateDelivery


class CreateDeliveryTest(TestCase):

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
            'line_items': [
                {
                    'id': 1,
                    'meta_data': [{
                        'id': 172,
                        'key': '_vendor_id',
                        'value': '6',
                        'display_key': 'Store',
                        'display_value': 'Quèviure'
                    }]
                },
                {
                    'id': 2,
                    'meta_data': [{
                        'id': 182,
                        'key': '_vendor_id',
                        'value': '5',
                        'display_key': 'Store',
                        'display_value': 'A granel'
                    }]
                }
            ]
        }

    def test_shipment(self):
        body = CreateDelivery(self.order).body()
        delivery = body['envios'][0]

        self.assertDictEqual(self.shipment_attrs(delivery), {
            'numPedido': 'xxx',
            'bultos': 1,
            'kilos': 1.0,
            'tipoServicio': '',
            'reembolso': 0.0,
            'observaciones': 'delivery testing',
        })

    def test_sender(self):
        body = CreateDelivery(self.order).body()
        deliveries = body['envios']

        self.assertDictEqual(self.sender_attrs(deliveries[0]), {
            'nombreRemi': 'Quèviure',
            'apellidoRemi': '6',
            'numeroCalleRemi': '',
            'direccionRemi': 'C/ La Zona, 1',
            'codPostalRemi': '08186',
            'poblacionRemi': 'Barcelona',
            'provinciaRemi': 'Barcelona',
            'paisRemi': 'ES',
            'emailRemi': 'lazona@opcions.org',
            'telefonoRemi': '+34518888191',
        })

        self.assertDictEqual(self.sender_attrs(deliveries[1]), {
            'nombreRemi': 'A granel',
            'apellidoRemi': '5',
            'numeroCalleRemi': '',
            'direccionRemi': 'C/ La Zona, 1',
            'codPostalRemi': '08186',
            'poblacionRemi': 'Barcelona',
            'provinciaRemi': 'Barcelona',
            'paisRemi': 'ES',
            'emailRemi': 'lazona@opcions.org',
            'telefonoRemi': '+34518888191',
        })

    def test_recipient(self):
        body = CreateDelivery(self.order).body()
        deliveries = body['envios']

        self.assertDictEqual(self.recipient_attrs(deliveries[0]), {
            'nombreDesti': 'James',
            'apellidoDesti': 'Bond',
            'direccionDesti': 'Address 1',
            'direccionAdicionalDesti': 'address 2',
            'numeroCalleDesti': '',
            'codPostalDesti': '08025',
            'poblacionDesti': 'Barcelona',
            'provinciaDesti': 'Barcelona',
            'paisDesti': 'ES',
            'telefonoDesti': '+34666554433',
            'emailDesti': 'email@example.com',
        })

    @patch('koiki.create_delivery.Sender')
    def test_body_calls_sender(self, MockSender):
        CreateDelivery(self.order).body()
        MockSender().to_dict.assert_called()

    @patch('koiki.create_delivery.Recipient')
    def test_body_calls_recipient(self, MockRecipient):
        CreateDelivery(self.order).body()
        MockRecipient().to_dict.assert_called()

    def test_url(self):
        self.assertEqual(CreateDelivery(self.order).url(), '/altaEnvios')

    def shipment_attrs(self, deliveries):
        other_attrs = {}
        for key, value in deliveries.items():
            if not key.endswith('Desti') and not key.endswith('Remi'):
                other_attrs[key] = value

        return other_attrs

    def recipient_attrs(self, deliveries):
        recipient_attrs = {}
        for key, value in deliveries.items():
            if key.endswith('Desti'):
                recipient_attrs[key] = value

        return recipient_attrs

    def sender_attrs(self, deliveries):
        sender_attrs = {}
        for key, value in deliveries.items():
            if key.endswith('Remi'):
                sender_attrs[key] = value

        return sender_attrs
