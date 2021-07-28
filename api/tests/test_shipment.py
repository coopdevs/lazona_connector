from unittest.mock import patch
import responses
from django.test import TestCase

from api.serializers import OrderSerializer
from api.tasks import create_or_update_delivery
from api.models import Shipment, ShipmentStatus
import koiki.vars


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
                }
            ],
        }

        responses.add(
            responses.GET,
            f"{koiki.vars.wcfmmp_host}/wp-json/wcfmmp/v1/settings/id/6",
            status=200,
            json={
                "phone": "",
                "address": {
                    "street_1": "",
                    "street_2": "",
                    "city": "",
                    "zip": "",
                    "country": "ES",
                    "state": "",
                },
            },
        )

        responses.add(
            responses.GET,
            f"{koiki.vars.wp_host}/wp-json/wp/v2/users/6?context=edit",
            status=200,
            content_type="application/json",
            json={
                "id": 6,
                "username": "Queviure",
                "email": "test@test.es",
                "roles": ["testrole"],
            },
        )

    @responses.activate
    @patch("koiki.email.EmailMessage", autospec=True)
    def test_create_shipment_successful(self, mock_email):
        responses.add(
            responses.POST,
            f"{koiki.vars.host}/rekis/api/altaEnvios",
            status=200,
            json={
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
            },
        )

        serializer = OrderSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())

        order = serializer.validated_data
        mock_email.send.return_value = True
        create_or_update_delivery(order)
        self.assertEqual(Shipment.objects.all().count(), 1)

        shipment = Shipment.objects.first()
        self.assertEqual(shipment.delivery_id, "yyy")
        self.assertEqual(shipment.order_id, 33)
        self.assertEqual(shipment.vendor_id, 6)
        self.assertTrue("(wc_order:33, vendor:6)" in str(shipment))
        self.assertEqual(shipment.label_url, "pdf_barcodes/123.pdf")
        self.assertEqual(shipment.status, ShipmentStatus.LABEL_SENT)

    @responses.activate
    @patch("koiki.email.EmailMessage", autospec=True)
    def test_create_shipment_failed(self, mock_email):
        responses.add(
            responses.POST,
            f"{koiki.vars.host}/rekis/api/altaEnvios",
            status=200,
            json={
                "respuesta": "102",
                "mensaje": "ERROR",
                "envios": [{"numPedido": "124", "respuesta": "102", "mensaje": "Missing field X"}],
            },
        )

        serializer = OrderSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())

        order = serializer.validated_data
        mock_email.send.return_value = True
        create_or_update_delivery(order)
        self.assertEqual(Shipment.objects.all().count(), 1)

        shipment = Shipment.objects.first()

        self.assertEqual(shipment.delivery_id, "")
        self.assertEqual(shipment.order_id, 33)
        self.assertEqual(shipment.vendor_id, 6)
        self.assertTrue("(wc_order:33, vendor:6)" in str(shipment))
        self.assertEqual(shipment.label_url, "")
        self.assertEqual(shipment.status, ShipmentStatus.ERROR_FROM_BODY)
