from unittest.mock import patch
import httpretty
from django.utils import timezone
import json
import ast
from django.test import TestCase
from api.serializers import OrderSerializer
from api.tasks import create_or_update_delivery
from api.models import Shipment, ShipmentStatus, ShipmentMethod
import lazona_connector.vars


class ShipmentTests(TestCase):
    def setUp(self):
        Shipment.objects.all().delete()

        self.data = {
            "id": 33,
            "order_key": "xxx",
            "customer_note": "",
            "shipping": {
                "first_name": "John",
                "last_name": "Lennon",
                "address_1": "Beatles Street 66",
                "address_2": "",
                "postcode": "08032",
                "city": "Barcelona",
                "state": "Barcelona",
                "country": "ES",
            },
            "billing": {"phone": "666666666", "email": "lennon@example.com"},
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
                },
                {
                    "id": 18,
                    "quantity": 1,
                    "name": "Producte 2",
                    "meta_data": [
                        {
                            "id": 173,
                            "key": "_vendor_id",
                            "value": "7",
                            "display_key": "Store",
                            "display_value": "A granel",
                        }
                    ],
                }
            ],
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
                },
                {
                    "id": 55,
                    "method_title": "Recollida en botiga",
                    "method_id": "local_pickup",
                    "meta_data": [{
                        "id": 173,
                        "key": "vendor_id",
                        "value": "7",
                        "display_key": "Store",
                        "display_value": "Quèviure",
                    }]
                }
            ],
        }
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
                    "email": "test@test.es",
                    "roles": ["testrole"],
                }
            ),
        )

    @patch("koiki.email.EmailMessage", autospec=True)
    def test_create_shipment_successful(self, mock_email):
        httpretty.register_uri(
            httpretty.POST,
            f"{lazona_connector.vars.koiki_host}/rekis/api/altaEnvios",
            status=200,
            content_type="text/json",
            body=json.dumps(
                {
                    "respuesta": "101",
                    "mensaje": "OK",
                    "envios": [
                        {
                            "numPedido": "123",
                            "codBarras": "yyy",
                            "etiqueta": "abcd",
                            "respuesta": "101",
                            "mensaje": "OK",
                        }
                    ],
                }
            ),
        )

        serializer = OrderSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())
        previous_time = timezone.now()
        order = serializer.validated_data
        mock_email.send.return_value = True
        create_or_update_delivery(order)
        self.assertEqual(Shipment.objects.all().count(), 2)

        shipment_koiki = Shipment.objects.filter(vendor_id=6).first()
        self.assertEqual(shipment_koiki.delivery_id, "yyy")
        self.assertEqual(shipment_koiki.order_id, 33)
        self.assertEqual(shipment_koiki.method, ShipmentMethod.KOIKI)
        self.assertTrue("(wc_order:33, vendor:6)" in str(shipment_koiki))
        self.assertEqual(shipment_koiki.label_url, "pdf_barcodes/123.pdf")
        self.assertEqual(shipment_koiki.status, ShipmentStatus.LABEL_SENT)
        self.assertEqual(shipment_koiki.delivery_message, "OK")
        delivery_req_body = json.loads(httpretty.last_request().body)["envios"][0]
        self.assertEqual(ast.literal_eval(shipment_koiki.req_body), delivery_req_body)
        self.assertEqual(ast.literal_eval(shipment_koiki.req_body)["paisRemi"], "ES")
        self.assertEqual(ast.literal_eval(shipment_koiki.req_body)["emailRemi"], "test@test.es")

        shipment_local = Shipment.objects.filter(vendor_id=7).first()
        self.assertEqual(shipment_local.order_id, 33)
        self.assertEqual(shipment_local.status, ShipmentStatus.DELIVERED)
        self.assertEqual(shipment_local.method, ShipmentMethod.LOCAL_PICKUP)
        self.assertGreater(shipment_local.updated_at, previous_time)

    @patch("koiki.email.EmailMessage", autospec=True)
    def test_create_shipment_failed(self, mock_email):
        httpretty.register_uri(
            httpretty.POST,
            f"{lazona_connector.vars.koiki_host}/rekis/api/altaEnvios",
            status=200,
            content_type="text/json",
            body=json.dumps(
                {
                    "respuesta": "102",
                    "mensaje": "ERROR",
                    "envios": [
                        {"numPedido": "124", "respuesta": "102", "mensaje": "Missing field X"}
                    ],
                }
            ),
        )

        serializer = OrderSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())

        order = serializer.validated_data
        mock_email.send.return_value = True
        create_or_update_delivery(order)
        self.assertEqual(Shipment.objects.all().count(), 2)

        shipment_koiki = Shipment.objects.filter(vendor_id=6).first()

        self.assertEqual(shipment_koiki.delivery_id, "")
        self.assertEqual(shipment_koiki.order_id, 33)
        self.assertEqual(shipment_koiki.method, ShipmentMethod.KOIKI)
        self.assertTrue("(wc_order:33, vendor:6)" in str(shipment_koiki))
        self.assertEqual(shipment_koiki.label_url, "")
        self.assertEqual(shipment_koiki.status, ShipmentStatus.ERROR_FROM_BODY)
        self.assertEqual(shipment_koiki.delivery_message, "Missing field X")

        shipment_local = Shipment.objects.filter(vendor_id=7).first()
        self.assertEqual(shipment_local.order_id, 33)
        self.assertEqual(shipment_local.status, ShipmentStatus.DELIVERED)
        self.assertEqual(shipment_local.method, ShipmentMethod.LOCAL_PICKUP)
