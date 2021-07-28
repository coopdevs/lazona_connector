from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from unittest.mock import patch
from tests_support.env_tests_support import EnvTestsSupport
from api.serializers import CustomerSerializer
import os
from django.conf import settings
settings.CELERY_ALWAYS_EAGER = True


@patch.dict(os.environ, EnvTestsSupport.to_dict())
class CustomerViewTests(TestCase):
    def setUp(self):
        self.url = reverse("deliveries:update_customer_if_partner")
        self.data = {
            "id": 1,
            "email": "partner@email.com",
            "first_name": "Test",
            "last_name": "test",
            "role": "customer",
            "username": "test.test",
            "is_paying_customer": False,
        }

        self.user = User.objects.create_superuser("admin", "admin@example.com", "pass")

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    @patch("api.tasks.update_customer_if_is_partner.delay", autospec=True)
    def test_successful_request(self, update_customer_if_is_partner):
        update_customer_if_is_partner.return_value = True
        serializer = CustomerSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())

        token = Token.objects.create(key="test token", user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        response = self.client.post(self.url, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_request(self):
        response = self.client.post(self.url, {})
        serializer = CustomerSerializer(data={})
        self.assertFalse(serializer.is_valid())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("api.tasks._check_customer_is_partner", autospec=True)
    def test_unauthenticated_request(self, mock_check_customer_is_partner):
        mock_check_customer_is_partner.return_value = True
        self.client.force_authenticate(user=None)
        response = self.client.post(self.url, self.data, format="json")

        self.assertEqual(
            response.content, b'{"detail":"Authentication credentials were not provided."}'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
