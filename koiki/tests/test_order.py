from unittest import TestCase
from unittest.mock import patch
from koiki.order import Order
from tests_support.env_tests_support import EnvTestsSupport


class OrderTest(TestCase):

    def setUp(self):
        self.env = patch.dict('os.environ',EnvTestsSupport.to_dict())
        self.data = {
            'id': 33,
            'order_key': '123x',
            'customer_note': 'dummy customer note',
            'line_items': [{
                'id': 17,
                'quantity': 1,
                'name': 'Suc Taronja 1l',
                'meta_data': [{
                    'id': 172,
                    'key': '_vendor_id',
                    'value': '6',
                    'display_key': 'Store',
                    'display_value': 'Quèviure'
                }]
            }]
        }

    def test_to_dict(self):
        order = Order(self.data)

        self.assertEqual(order.to_dict(), {
            'numPedido': self.data['order_key'],
            'bultos': 1,
            'kilos': 1.0,
            'tipoServicio': '',
            'reembolso': 0.0,
            'observaciones': 'dummy customer note'
        })
