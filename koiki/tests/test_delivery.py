from django.test import TestCase
from unittest.mock import MagicMock
from koiki.delivery import Delivery


class DeliveryTests(TestCase):
    def test_attributes(self):
        data = {
            "order_id": 33,
            "numPedido": "456_xxx",
            "codBarras": "JJD00026901003806220001",
            "etiqueta": "abc",
        }
        vendor = MagicMock()
        delivery = Delivery(data, vendor)

        self.assertEqual(
            delivery.to_dict(),
            {
                "order_id": 33,
                "number": "456_xxx",
                "barcode": "JJD00026901003806220001",
                "label": "abc",
            },
        )
