from django.test import TestCase
from unittest.mock import patch, MagicMock

from api.serializers import CustomerSerializer
from api.tasks import check_customer_is_partner
from sugarcrm import CrmError


class TasksCustomerTests(TestCase):
    def setUp(self):
        self.data = {
            "id": "xxx",
            "date_created": "2021-05-06T13:06:18",
            "date_created_gmt": "2021-05-06T11:06:18",
            "date_modified": "2021-05-06T13:06:18",
            "date_modified_gmt": "2021-05-06T11:06:18",
            "email": "partner@email.com",
            "first_name": "Test",
            "last_name": "test",
            "role": "customer",
            "username": "test.test",
            "billing": {
                "first_name": "Test",
                "last_name": "test",
                "company": "",
                "address_1": "sdadsad",
                "address_2": "adsadsadasdadsa",
                "city": "sadasdasdadsa",
                "postcode": "33333",
                "country": "ES",
                "state": "B",
                "email": "xxxx@xxxxx.com",
                "phone": "4234324324234",
            },
            "shipping": {
                "first_name": "Test",
                "last_name": "test",
                "company": "",
                "address_1": "xx",
                "address_2": "xx",
                "city": "xx",
                "postcode": "xx",
                "country": "ES",
                "state": "B",
            },
            "is_paying_customer": False,
            "avatar_url": "http://1.gravatar.com/avatar/xx",
            "meta_data": [{"id": 1, "key": "shipping_method"}],
        }

    @patch("api.tasks.CrmClient", autospec=True)
    def test_failure(self, mock_client):
        mock_client.check_customer_is_partner.side_effect = CrmError

        serializer = CustomerSerializer(data=self.data)
        serializer.is_valid()
        customer = serializer.validated_data
        with self.assertRaises(CrmError):
            mock_client.check_customer_is_partner(customer)

    @patch("api.tasks.CrmClient", autospec=True)
    def test_success(self, mock_client):
        mock_client.check_customer_is_partner.return_value = MagicMock()

        serializer = CustomerSerializer(data=self.data)
        serializer.is_valid()
        customer = serializer.validated_data
        result = check_customer_is_partner(customer)

        self.assertIn("is_partner", result)
