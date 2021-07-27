from django.test import TestCase
from unittest.mock import patch,MagicMock
from koiki.delivery import Delivery
from tests_support.env_tests_support import EnvTestsSupport


class DeliveryTests(TestCase):
    def setUp(self):
        self.env = patch.dict('os.environ',EnvTestsSupport.to_dict())
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
