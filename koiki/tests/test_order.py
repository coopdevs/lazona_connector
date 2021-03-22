from unittest import TestCase

from koiki.order import Order


class OrderTest(TestCase):

    def setUp(self):
        self.data = {
            'order_key': '123x',
            'customer_note': 'dummy customer note'
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
