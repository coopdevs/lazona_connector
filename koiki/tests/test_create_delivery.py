from unittest import TestCase
from unittest.mock import patch

from koiki.create_delivery import CreateDelivery


class CreateDeliveryTest(TestCase):

    maxDiff = None

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
                    'quantity': 1,
                    'meta_data': [{
                        'id': 182,
                        'key': '_vendor_id',
                        'value': '5',
                        'display_key': 'Store',
                        'display_value': 'A granel'
                    }]
                },
                {
                    'id': 2,
                    'quantity': 1,
                    'meta_data': [{
                        'id': 172,
                        'key': '_vendor_id',
                        'value': '6',
                        'display_key': 'Store',
                        'display_value': 'Quèviure'
                    }]
                },
                {
                    'id': 3,
                    'quantity': 1,
                    'meta_data': [{
                        'id': 123,
                        'key': '_vendor_id',
                        'value': '5',
                        'display_key': 'Store',
                        'display_value': 'A granel'
                    }]
                }
            ]
        }

    def test_delivery(self):
        line_items = [
            {
                'quantity': 1,
                'meta_data': [{
                    'id': 182,
                    'key': '_vendor_id',
                    'value': '5',
                    'display_key': 'Store',
                    'display_value': 'A granel'
                }]
            },
            {
                'quantity': 1,
                'meta_data': [{
                    'id': 123,
                    'key': '_vendor_id',
                    'value': '5',
                    'display_key': 'Store',
                    'display_value': 'A granel'
                }]
            }
        ]
        vendor_metadata = {
            'id': 123,
            'key': '_vendor_id',
            'value': '5',
            'display_key': 'Store',
            'display_value': 'A granel'
        }
        delivery = CreateDelivery(self.order)._delivery(line_items, vendor_metadata)

        self.assertDictContainsSubset({'bultos': 2}, delivery)
        self.assertDictContainsSubset({'nombreRemi': 'A granel'}, delivery)

    def test_vendor(self):
        metadata = [
            {
                'id': 123,
                'key': '_vendor_id',
                'value': '5',
                'display_key': 'Store',
                'display_value': 'A granel'
            }
        ]
        vendor = CreateDelivery(self.order)._vendor_id(metadata)
        self.assertEquals(vendor, '5')

    def test_build_structure(self):
        by_vendor = CreateDelivery(self.order)._by_vendor()

        self.assertListEqual(by_vendor['5'], [
            {
                'id': 1,
                'quantity': 1,
                'meta_data': [{
                    'id': 182,
                    'key': '_vendor_id',
                    'value': '5',
                    'display_key': 'Store',
                    'display_value': 'A granel'
                }]
            },
            {
                'id': 3,
                'quantity': 1,
                'meta_data': [{
                    'id': 123,
                    'key': '_vendor_id',
                    'value': '5',
                    'display_key': 'Store',
                    'display_value': 'A granel'
                }]
            }
        ])

        self.assertListEqual(by_vendor['6'], [
            {
                'id': 2,
                'quantity': 1,
                'meta_data': [{
                    'id': 172,
                    'key': '_vendor_id',
                    'value': '6',
                    'display_key': 'Store',
                    'display_value': 'Quèviure'
                }]
            }
        ])

    def test_deliveries(self):
        body = CreateDelivery(self.order).body()
        deliveries = body['envios']

        self.assertDictContainsSubset({
            'numPedido': 'xxx',
            'bultos': 2,
            'kilos': 0.0,
            'tipoServicio': '',
            'reembolso': 0.0,
            'observaciones': 'delivery testing',
            'nombreRemi': 'A granel',
            'apellidoRemi': '',
            'numeroCalleRemi': '',
            'direccionRemi': 'C/ La Zona, 1',
            'codPostalRemi': '08186',
            'poblacionRemi': 'Barcelona',
            'provinciaRemi': 'Barcelona',
            'paisRemi': 'ES',
            'emailRemi': 'lazona@opcions.org',
            'telefonoRemi': '518888191'
        }, deliveries[0])

        self.assertDictContainsSubset({
            'numPedido': 'xxx',
            'bultos': 1,
            'kilos': 0.0,
            'tipoServicio': '',
            'reembolso': 0.0,
            'observaciones': 'delivery testing',
            'nombreRemi': 'Quèviure',
            'apellidoRemi': '',
            'numeroCalleRemi': '',
            'direccionRemi': 'C/ La Zona, 1',
            'codPostalRemi': '08186',
            'poblacionRemi': 'Barcelona',
            'provinciaRemi': 'Barcelona',
            'paisRemi': 'ES',
            'emailRemi': 'lazona@opcions.org',
            'telefonoRemi': '518888191',
        }, deliveries[1])

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
