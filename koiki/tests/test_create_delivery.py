from unittest import TestCase
import httpretty
import json
from koiki.order import Order
from koiki.delivery_create import CreateDelivery
import lazona_connector.vars


class CreateDeliveryTest(TestCase):

    maxDiff = None

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

        httpretty.register_uri(
            httpretty.GET,
            f"{lazona_connector.vars.wcfmmp_host}/wp-json/wcfmmp/v1/settings/id/5",
            status=200,
            content_type="application/json",
            body=json.dumps(
                {
                    "phone": "93333333",
                    "address": {
                        "street_1": "Sant Antoni Maria Claret, 175",
                        "street_2": "",
                        "city": "Barcelona",
                        "zip": "08041",
                        "country": "ES",
                        "state": "",
                    },
                }
            ),
        )
        httpretty.register_uri(
            httpretty.GET,
            f"{lazona_connector.vars.wp_host}/wp-json/wp/v2/users/5?context=edit",
            status=200,
            content_type="application/json",
            body=json.dumps({
                    "id": 5,
                    "username": "A Granel",
                    "email": "detergents@agranel.coop",
                    "roles": ["testrole"],
                }
            ),
        )

        httpretty.register_uri(
            httpretty.GET,
            f"{lazona_connector.vars.wcfmmp_host}/wp-json/wcfmmp/v1/settings/id/6",
            status=200,
            content_type="application/json",
            body=json.dumps(
                {
                    "phone": "",
                    "address": {
                        "street_1": "",
                        "street_2": "",
                        "city": "",
                        "zip": "",
                        "country": "ES",
                        "state": "",
                    },
                }
            ),
        )
        httpretty.register_uri(
            httpretty.GET,
            f"{lazona_connector.vars.wp_host}/wp-json/wp/v2/users/6?context=edit",
            status=200,
            content_type="application/json",
            body=json.dumps(
                {
                    "id": 6,
                    "username": "Queviure",
                    "email": "queviure@lazona.coop",
                    "roles": ["testrole"],
                }
            ),
        )

        body = CreateDelivery(Order(self.order)).body()
        deliveries = body['envios']

        self.assertEquals(len(deliveries), 2)

        self.assertDictContainsSubset({
            'numPedido': 'xxx',
            # TODO: Refactor we're forcing each vendor generates always 1 package.
            'bultos': 1,
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
            'paisRemi': 'ES',
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
        self.assertEqual(
            CreateDelivery(Order(self.order)).url(),
            f'{lazona_connector.vars.koiki_host}/rekis/api/altaEnvios'
        )
