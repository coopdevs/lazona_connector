from django.test import TestCase
from unittest.mock import patch, MagicMock

from api.serializers import OrderSerializer
from api.tasks import create_delivery
from koiki.error import Error


class TasksTests(TestCase):

    def setUp(self):
        self.data = {
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

    @patch('api.tasks.Client', autospec=True)
    def test_pdf_persistance(self, mock_client):
        mock_delivery = MagicMock(name='delivery')
        client = MagicMock(name='client')
        client.create_delivery.return_value = mock_delivery
        mock_delivery.print_pdf.return_value = MagicMock()

        mock_client.return_value = client

        serializer = OrderSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())
        order = serializer.validated_data
        create_delivery(order)

        mock_delivery.print_pdf.assert_called_once()

    @patch('api.tasks.Client', autospec=True)
    def test_failure(self, mock_client):
        client = MagicMock()
        client.create_delivery.return_value = Error({'mensaje': 'ERROR IN THE RECEIVED DATA'})
        mock_client.return_value = client

        serializer = OrderSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())
        order = serializer.validated_data
        result = create_delivery(order)

        self.assertEqual(result, {'error': 'ERROR IN THE RECEIVED DATA'})

    @patch('api.tasks.Client', autospec=True)
    def test_success(self, mock_client):
        client = MagicMock()
        client.create_delivery.return_value = MagicMock()
        mock_client.return_value = client

        serializer = OrderSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())
        order = serializer.validated_data
        result = create_delivery(order)

        self.assertEqual(result, {'success': 'all good'})
