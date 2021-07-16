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
            "mensaje": "message_test",
            "respuesta": "102"


        }
        vendor = MagicMock()
        delivery = Delivery(data, vendor)

        self.assertEqual(
            delivery.to_dict(),
            {
                "order_id": 33,
                "shipment_id": "456_xxx",
                "barcode": "JJD00026901003806220001",
                "label": "abc",
                "message": "message_test",
                "response": "102"
            },
        )
