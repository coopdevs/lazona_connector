from unittest import TestCase
from koiki.shipment import Shipment


class ShipmentTest(TestCase):

    maxDiff = None

    def setUp(self):
        self.order = {
            'order_key': 123,
            'customer_note': 'nota'
        }

    def test_to_dict(self):
        shipment = Shipment(self.order, packages=2)

        self.assertDictEqual(shipment.to_dict(), {
            'numPedido': 123,
            'observaciones': 'nota',
            'tipoServicio': '',
            'reembolso': 0.0,
            'kilos': 0.0,
            'bultos': 2
        })

    def test_default_packages(self):
        shipment = Shipment(self.order)

        self.assertDictEqual(shipment.to_dict(), {
            'numPedido': 123,
            'observaciones': 'nota',
            'tipoServicio': '',
            'reembolso': 0.0,
            'kilos': 0.0,
            'bultos': 1
        })
