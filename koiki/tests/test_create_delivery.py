from unittest import TestCase
import responses

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
                    'meta_data': [
                        {
                            'id': 173,
                            'key': '_wcfmmp_order_item_processed',
                            'value': '5',
                            'display_key': 'Store Order ID',
                            'display_value': '5'
                        },
                        {
                            'id': 172,
                            'key': '_vendor_id',
                            'value': '6',
                            'display_key': 'Store',
                            'display_value': 'Quèviure'
                        }
                    ],
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

    @responses.activate
    def test_body(self):
        responses.add(responses.GET, 'http://staging.lazona.coop/wp-json/wcfmmp/v1/settings/id/5', status=200, json={
            "store_email": "detergents@agranel.coop",
            "phone": "93333333",
            "address": {
                "street_1": "Sant Antoni Maria Claret, 175",
                "street_2": "",
                "city": "Barcelona",
                "zip": "08041",
                "country": "",
                "state": ""
            }
        })
        responses.add(responses.GET, 'http://staging.lazona.coop/wp-json/wcfmmp/v1/settings/id/6', status=200, json={
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

        body = CreateDelivery(self.order).body()
        deliveries = body['envios']

        self.assertEquals(len(deliveries), 2)

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
            'direccionRemi': 'Sant Antoni Maria Claret, 175',
            'codPostalRemi': '08041',
            'poblacionRemi': 'Barcelona',
            'provinciaRemi': '',
            'paisRemi': '',
            'emailRemi': 'detergents@agranel.coop',
            'telefonoRemi': '93333333'
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
            'direccionRemi': '',
            'codPostalRemi': '',
            'poblacionRemi': '',
            'provinciaRemi': '',
            'paisRemi': 'ES',
            'emailRemi': 'queviure@lazona.coop',
            'telefonoRemi': '',
        }, deliveries[1])

    def test_url(self):
        self.assertEqual(CreateDelivery(self.order).url(), '/altaEnvios')
