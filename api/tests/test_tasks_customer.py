from django.test import TestCase
from unittest.mock import patch, MagicMock

from api.serializers import CustomerSerializer
from api.tasks import _check_customer_is_partner


class TasksCustomerTests(TestCase):
    def setUp(self):
        self.data = {
            "id": 1,
            "email": "partner@email.com",
            "first_name": "Test",
            "last_name": "test",
            "role": "customer",
            "username": "test.test",
            "is_paying_customer": False,
        }

    @patch("api.tasks.Customer", autospec=True)
    def test_customer_with_no_roles(self, mock_client):
        mock_client.fetch.return_value = MagicMock()
        serializer = CustomerSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())
        customer = serializer.validated_data

        self.assertFalse(_check_customer_is_partner(customer["email"]))
