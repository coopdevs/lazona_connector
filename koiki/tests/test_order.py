from unittest import TestCase
from koiki.resources import KoikiOrder


class OrderTest(TestCase):
    def setUp(self):
        self.data = {
            "id": 33,
            "order_key": "123x",
            "customer_note": "dummy customer note",
            "shipping_lines": [
                {
                    "id": 54,
                    "method_title": "Enviament Koiki",
                    "method_id": "wcfmmp_product_shipping_by_zone",
                    "meta_data": [{
                        "id": 172,
                        "key": "vendor_id",
                        "value": "6",
                        "display_key": "Store",
                        "display_value": "Quèviure",
                    }]
                }
            ],
            "line_items": [
                {
                    "id": 17,
                    "quantity": 1,
                    "name": "Suc Taronja 1l",
                    "meta_data": [
                        {
                            "id": 172,
                            "key": "_vendor_id",
                            "value": "6",
                            "display_key": "Store",
                            "display_value": "Quèviure",
                        }
                    ],
                }
            ],
        }

    def test_to_dict(self):
        order = KoikiOrder(self.data)

        self.assertEqual(
            order.to_dict(),
            {
                "numPedido": self.data["order_key"],
                "bultos": 1,
                "kilos": 1.0,
                "tipoServicio": "",
                "reembolso": 0.0,
                "observaciones": "dummy customer note",
            },
        )
