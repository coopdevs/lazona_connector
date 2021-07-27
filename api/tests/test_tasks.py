from unittest.mock import patch, MagicMock
import responses
from django.test import TestCase

from api.serializers import OrderSerializer
from api.tasks import create_delivery
import koiki.vars
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

        responses.add(responses.GET, f'{koiki.vars.wcfmmp_host}/wp-json/wcfmmp/v1/settings/id/6',
                      status=200,
                      json={
                        "phone": "",
                        "address": {
                            "street_1": "",
                            "street_2": "",
                            "city": "",
                            "zip": "",
                            "country": "ES",
                            "state": ""
                        }
                      })

        responses.add(
                responses.GET,
                'https://wp_testing_host/wp-json/wp/v2/users/6?context=edit',
                status=200,
                content_type='application/json',
                json={
                    "id": 6,
                    "username": "Queviure",
                    "email": "test@test.es",
                    "roles": ["testrole"],
                }
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

        create_delivery(order)

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
        create_delivery(order)
        self.assertTrue(delivery._is_errored())

    @responses.activate
    @patch('koiki.email.EmailMessage', autospec=True)
    @patch('api.tasks.logger', autospec=True)
    def test_create_delivery_sends_email(self, mock_logger, mock_email):
        responses.add(responses.POST, 'https://testing_host/rekis/api/altaEnvios', status=200,
                      json={
                        'respuesta': '101',
                        'mensaje': 'OK',
                        'envios': [{'numPedido': '123', 'codBarras': 'yyy', 'etiqueta': 'abcd',
                                    'respuesta': '101', 'mensaje': 'OK'}]
                      })

        serializer = OrderSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())
        order = serializer.validated_data

        mock_email.send.return_value = True

        create_delivery(order)
        mock_logger.info.assert_called_once_with("Sending Koiki pdf to vendor with id 6")
        self.assertIn({'to': ['test@test.es']}, mock_email.call_args)
        message = mock_email.call_args[0][1]
        self.assertIn(f"{koiki.vars.wcfmmp_host}/area-privada/orders-details/33", message)

    @responses.activate
    @patch('koiki.email.EmailMessage', autospec=True)
    @patch('koiki.email.logger', autospec=True)
    def test_create_delivery_sends_error_email(self, mock_logger, mock_email):
        responses.add(responses.POST, 'https://testing_host/rekis/api/altaEnvios', status=200,
                      json={
                        'respuesta': '102',
                        'mensaje': 'ERROR',
                        'envios': [{'numPedido': '124', 'respuesta': '102',
                                    'mensaje': 'Missing field X'}]
                      })

        serializer = OrderSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())
        order = serializer.validated_data

        mock_email.send.return_value = True

        create_delivery(order)
        mock_logger.info.assert_called_once_with("Sending Koiki error to admins for order 33")
        self.assertIn({'to': ['admin@email.com']}, mock_email.call_args)
        message = mock_email.call_args[0][1]
        self.assertIn(f"{koiki.vars.wcfmmp_host}/area-privada/orders-details/33", message)
        self.assertIn("Missing field X", message)

    @responses.activate
    @patch('koiki.email.EmailMessage', autospec=True)
    @patch('koiki.email.logger', autospec=True)
    def test_create_delivery_sends_error_email_default_error(self, mock_logger, mock_email):
        responses.add(responses.POST, 'https://testing_host/rekis/api/altaEnvios', status=200,
                      json={
                        'respuesta': '102',
                        'mensaje': 'ERROR',
                        'envios': [{'numPedido': '124', 'respuesta': '102',
                                    'mensaje': ''}]
                      })

        serializer = OrderSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())
        order = serializer.validated_data
        mock_email.send.return_value = True

        create_delivery(order)
        message = mock_email.call_args[0][1]
        self.assertIn("Missatge d'error no proporcionat", message)
