from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
import httpretty


class DeliveryViewTests(TestCase):

    def setUp(self):
        self.url = reverse('deliveries:create')
        self.data = {
            'order_key': 'xxx',
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
            }
        }
        self.api_url = 'https://testing_host/rekis/api/altaEnvios'

        self.user = User.objects.create_superuser('admin', 'admin@example.com', 'pass')

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_successful_request(self):
        httpretty.register_uri(httpretty.POST, self.api_url, status=200, content_type='text/json')

        token = Token.objects.create(key='test token', user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.post(self.url, self.data, format='json')

        self.assertEqual(response.data, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unsuccessful_request(self):
        response = self.client.post(self.url, {})

        self.assertEqual(response.data['order_key'][0].code, 'required')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_request(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(self.url, {})

        self.assertEqual(response.content,
                         b'{"detail":"Authentication credentials were not provided."}')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('api.views.Client', autospec=True)
    def test_koiki_client_is_used(self, mock_koiki_client):
        httpretty.register_uri(httpretty.POST, self.api_url, status=200, content_type='text/json')

        response = self.client.post(self.url, self.data, format='json')

        mock_koiki_client.assert_called_once_with(self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @patch('api.views.Client.create_delivery', autospec=True)
    def test_koiki_create_delivery_is_called(self, mock_create_delivery):
        httpretty.register_uri(httpretty.POST, self.api_url, status=200, content_type='text/json')

        response = self.client.post(self.url, self.data, format='json')

        mock_create_delivery.assert_called()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
