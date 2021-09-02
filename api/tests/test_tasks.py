from unittest.mock import patch, MagicMock
import httpretty
import json
from django.test import TestCase
from api.serializers import OrderSerializer
from api.tasks import create_or_update_delivery
import lazona_connector.vars
from koiki.delivery import Delivery


class TasksTests(TestCase):

    def setUp(self):
        self.data = {
            'id': 33,
            'order_key': 'xxx',
            'customer_note': '',
            'shipping': {
                'first_name': 'John',
                'last_name': 'Lennon',
                'address_1': 'Beatles Street 66',
                'address_2': '',
                'postcode': '08032',
                'city': 'Barcelona',
                'state': 'Barcelona',
                'country': 'ES'
            },
            'billing': {
                'phone': '666666666',
                'email': 'lennon@example.com'
            },
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

    @patch('koiki.delivery.Delivery.print_pdf', autospec=True)
    @patch('koiki.email.SuccessDeliveryMail.send', autospec=True)
    @patch('api.tasks.Client', autospec=True)
    def test_delivery_successful(self, mock_client, mock_success_email, mock_print_pdf):
        client = MagicMock(name='client')
        vendor = MagicMock()
        delivery = Delivery({
            "respuesta": "101", "numPedido": "test", "order_id": 33, "codBarras": "CODBAR33"},
            vendor)
        client.create_delivery.return_value = [delivery]
        mock_print_pdf.return_value = "pdf_barcodes/test.pdf"
        mock_client.return_value = client
        self.assertEqual(delivery.get_data_val("barcode"), "CODBAR33")
        serializer = OrderSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())
        order = serializer.validated_data

        create_or_update_delivery(order)

        mock_success_email.assert_called_once()

    @patch('api.tasks.Client', autospec=True)
    def test_failure(self, mock_client):
        client = MagicMock()
        vendor = MagicMock()
        delivery = Delivery({
            "respuesta": "102",
            "mensaje": "ERROR IN THE RECEIVED DATA", "numPedido": "test", "order_id": 33},
            vendor)
        client.create_delivery.return_value = [delivery]
        mock_client.return_value = client

        serializer = OrderSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())
        order = serializer.validated_data
        create_or_update_delivery(order)
        self.assertTrue(delivery._is_errored())

    @patch('koiki.email.EmailMessage', autospec=True)
    @patch('api.tasks.logger', autospec=True)
    def test_create_delivery_sends_email(self, mock_logger, mock_email):
        httpretty.register_uri(
            httpretty.POST,
            f"{lazona_connector.vars.koiki_host}/rekis/api/altaEnvios",
            status=200,
            content_type="text/json",
            body=json.dumps(
                {
                    'respuesta': '101',
                    'mensaje': 'OK',
                    'envios': [{
                        'numPedido': '123',
                        'codBarras': 'yyy',
                        'etiqueta': 'abcd',
                        'respuesta': '101',
                        'mensaje': 'OK'
                    }]
                }
            ),
        )

        serializer = OrderSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())
        order = serializer.validated_data

        mock_email.send.return_value = True

        create_or_update_delivery(order)
        mock_logger.info.assert_called_once_with("Sending Koiki pdf to vendor with id 6")
        self.assertIn({'to': ['test@test.es']}, mock_email.call_args)
        message = mock_email.call_args[0][1]
        self.assertIn(
            f"{lazona_connector.vars.wcfmmp_host}/area-privada/orders-details/33",
            message
        )

    @patch('koiki.email.EmailMessage', autospec=True)
    @patch('koiki.email.logger', autospec=True)
    def test_create_delivery_sends_error_email(self, mock_logger, mock_email):
        httpretty.register_uri(
            httpretty.POST,
            f"{lazona_connector.vars.koiki_host}/rekis/api/altaEnvios",
            status=200,
            content_type="text/json",
            body=json.dumps({
                'respuesta': '102',
                'mensaje': 'ERROR',
                'envios': [{
                    'numPedido': '124',
                    'respuesta': '102',
                    'mensaje': 'Missing field X'
                }]
            })
        )

        serializer = OrderSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())
        order = serializer.validated_data

        mock_email.send.return_value = True

        create_or_update_delivery(order)
        mock_logger.info.assert_called_once_with("Sending Koiki error to admins for order 33")
        self.assertIn({'to': lazona_connector.vars.error_mail_recipients}, mock_email.call_args)
        message = mock_email.call_args[0][1]
        self.assertIn(
            f"{lazona_connector.vars.wcfmmp_host}/area-privada/orders-details/33",
            message
        )
        self.assertIn("Missing field X", message)

    @patch('koiki.email.EmailMessage', autospec=True)
    @patch('koiki.email.logger', autospec=True)
    def test_create_delivery_sends_error_email_default_error(self, mock_logger, mock_email):
        httpretty.register_uri(
            httpretty.POST,
            f"{lazona_connector.vars.koiki_host}/rekis/api/altaEnvios",
            status=200,
            content_type="text/json",
            body=json.dumps({
                'respuesta': '102',
                'mensaje': 'ERROR',
                'envios': [{
                    'numPedido': '124',
                    'respuesta': '102',
                    'mensaje': ''
                }]
            })
        )

        serializer = OrderSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())
        order = serializer.validated_data
        mock_email.send.return_value = True

        create_or_update_delivery(order)
        message = mock_email.call_args[0][1]
        self.assertIn("Missatge d'error no proporcionat", message)
