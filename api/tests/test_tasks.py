from django.utils import timezone
from unittest.mock import patch, MagicMock
import responses
import httpretty
import json
from django.test import TestCase
from api.serializers import OrderSerializer
from api.tasks import create_or_update_delivery, update_delivery_status
import lazona_connector.vars
from koiki.delivery import Delivery
from api.models import Shipment, ShipmentStatus


class TasksTests(TestCase):
    def setUp(self):
        Shipment.objects.all().delete()
        self.shipment = Shipment.objects.create(
            delivery_id="111",
            order_id=2,
            vendor_id=5,
            label_url="my_pdf_url",
            status="",
        )

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
            f"{lazona_connector.vars.wcfmmp_host}/wp-json/wcfmmp/v1/settings/id/6",
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
            f"{lazona_connector.vars.wp_host}/wp-json/wp/v2/users/6?context=edit",
            status=200,
            content_type="application/json",
            json={
                "id": 6,
                "username": "Queviure",
                "email": "test@test.es",
                "roles": ["testrole"],
            },
        )

    @patch("koiki.delivery.Delivery.print_pdf", autospec=True)
    @patch("koiki.email.SuccessDeliveryMail.send", autospec=True)
    @patch("api.tasks.Client", autospec=True)
    def test_delivery_successful(self, mock_client, mock_success_email, mock_print_pdf):
        client = MagicMock(name="client")
        vendor = MagicMock()
        delivery = Delivery(
            {"respuesta": "101", "numPedido": "test", "order_id": 33, "codBarras": "CODBAR33"},
            vendor,
        )
        client.create_delivery.return_value = [delivery]
        mock_print_pdf.return_value = "pdf_barcodes/test.pdf"
        mock_client.return_value = client
        self.assertEqual(delivery.get_data_val("barcode"), "CODBAR33")
        serializer = OrderSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())
        order = serializer.validated_data

        create_or_update_delivery(order)

        mock_success_email.assert_called_once()

    @patch("api.tasks.Client", autospec=True)
    def test_failure(self, mock_client):
        client = MagicMock()
        vendor = MagicMock()
        delivery = Delivery(
            {
                "respuesta": "102",
                "mensaje": "ERROR IN THE RECEIVED DATA",
                "numPedido": "test",
                "order_id": 33,
            },
            vendor,
        )
        client.create_delivery.return_value = [delivery]
        mock_client.return_value = client

        serializer = OrderSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())
        order = serializer.validated_data
        create_or_update_delivery(order)
        self.assertTrue(delivery._is_errored())

    @responses.activate
    @patch("koiki.email.EmailMessage", autospec=True)
    @patch("api.tasks.logger", autospec=True)
    def test_create_delivery_sends_email(self, mock_logger, mock_email):
        responses.add(
            responses.POST,
            f"{lazona_connector.vars.koiki_host}/rekis/api/altaEnvios",
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
        mock_logger.info.assert_called_once_with("Sending Koiki pdf to vendor with id 6")
        self.assertIn({"to": ["test@test.es"]}, mock_email.call_args)
        message = mock_email.call_args[0][1]
        self.assertIn(
            f"{lazona_connector.vars.wcfmmp_host}/area-privada/orders-details/33", message
        )

    @responses.activate
    @patch("koiki.email.EmailMessage", autospec=True)
    @patch("koiki.email.logger", autospec=True)
    def test_create_delivery_sends_error_email(self, mock_logger, mock_email):
        responses.add(
            responses.POST,
            f"{lazona_connector.vars.koiki_host}/rekis/api/altaEnvios",
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
        mock_logger.info.assert_called_once_with("Sending Koiki error to admins for order 33")
        self.assertIn({"to": lazona_connector.vars.error_mail_recipients}, mock_email.call_args)
        message = mock_email.call_args[0][1]
        self.assertIn(
            f"{lazona_connector.vars.wcfmmp_host}/area-privada/orders-details/33", message
        )
        self.assertIn("Missing field X", message)

    @responses.activate
    @patch("koiki.email.EmailMessage", autospec=True)
    @patch("koiki.email.logger", autospec=True)
    def test_create_delivery_sends_error_email_default_error(self, mock_logger, mock_email):
        responses.add(
            responses.POST,
            f"{lazona_connector.vars.koiki_host}/rekis/api/altaEnvios",
            status=200,
            json={
                "respuesta": "102",
                "mensaje": "ERROR",
                "envios": [{"numPedido": "124", "respuesta": "102", "mensaje": ""}],
            },
        )

        serializer = OrderSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())
        order = serializer.validated_data
        mock_email.send.return_value = True

        create_or_update_delivery(order)
        message = mock_email.call_args[0][1]
        self.assertIn("Missatge d'error no proporcionat", message)

    @patch("koiki.email.EmailMessage", autospec=True)
    def test_update_delivery_status_response_error(self, mock_email):
        httpretty.register_uri(
            httpretty.POST,
            f"{lazona_connector.vars.koiki_tracking_host}/kis/api/v1/service/track/see",
            status=200,
            content_type="text/json",
            body=json.dumps({"error": {"code": 101, "message": "CODE NOT FOUND"}}),
        )

        mock_email.send.return_value = True
        self.shipment.delivery_message = ""
        self.shipment.status = ""
        previous_time = timezone.now()
        self.shipment.tracking_status_created_at = previous_time
        self.shipment.save()
        update_delivery_status(self.shipment.delivery_id, email_notify=True)
        self.shipment.refresh_from_db()
        self.assertEqual(self.shipment.status, ShipmentStatus.ERROR_FROM_TRACKING)
        self.assertEqual(self.shipment.delivery_message, "CODE NOT FOUND")
        self.assertIsNone(self.shipment.tracking_status_created_at)
        self.assertGreater(self.shipment.tracking_updated_at, previous_time)

        self.assertIn({"to": lazona_connector.vars.error_mail_recipients}, mock_email.call_args)
        message = mock_email.call_args[0][1]
        self.assertIn("CODE NOT FOUND", message)

    @patch("koiki.email.EmailMessage", autospec=True)
    def test_update_delivery_status_unknown_code(self, mock_email):
        httpretty.register_uri(
            httpretty.POST,
            f"{lazona_connector.vars.koiki_tracking_host}/kis/api/v1/service/track/see",
            status=200,
            content_type="text/json",
            body=json.dumps(
                {
                    "result": [
                        {
                            "servicio": "111",
                            "codEstado": "Unknown state",
                            "date": "2021-07-26T07:09:21+0000",
                            "code": 9999,
                        },
                    ]
                }
            ),
        )

        self.shipment.delivery_message = ""
        self.shipment.status = ""
        self.shipment.save()
        previous_time = timezone.now()
        update_delivery_status(self.shipment.delivery_id, email_notify=False)
        self.shipment.refresh_from_db()
        mock_email.send.assert_not_called()

        self.assertEqual(self.shipment.status, ShipmentStatus.ERROR_FROM_TRACKING)
        self.assertEqual(
            self.shipment.delivery_message, "Unknown state. Doesn't match any shipment status"
        )
        self.assertGreater(self.shipment.tracking_updated_at, previous_time)
        self.assertEqual(
            self.shipment.tracking_status_created_at.strftime("%Y-%m-%dT%H:%M:%S+0000"),
            "2021-07-26T07:09:21+0000",
        )

    def test_update_delivery_status_success(self):
        httpretty.register_uri(
            httpretty.POST,
            f"{lazona_connector.vars.koiki_tracking_host}/kis/api/v1/service/track/see",
            status=200,
            content_type="text/json",
            body=json.dumps(
                {
                    "result": [
                        {
                            "servicio": "111",
                            "codEstado": "Envío entregado",
                            "date": "2021-07-26T09:49:37+0000",
                            "code": 108,
                        },
                        {
                            "servicio": "111",
                            "codEstado": "Envio en Reparto",
                            "date": "2021-07-26T07:09:21+0000",
                            "code": 901,
                        },
                    ]
                }
            ),
        )

        self.shipment.delivery_message = ""
        self.shipment.status = ""
        self.shipment.save()
        previous_time = timezone.now()
        update_delivery_status(self.shipment.delivery_id, email_notify=False)
        self.shipment.refresh_from_db()

        self.assertEqual(self.shipment.status, ShipmentStatus.DELIVERED)
        self.assertEqual(self.shipment.delivery_message, "Envío entregado")
        self.assertGreater(self.shipment.tracking_updated_at, previous_time)
        self.assertEqual(
            self.shipment.tracking_status_created_at.strftime("%Y-%m-%dT%H:%M:%S+0000"),
            "2021-07-26T09:49:37+0000",
        )
