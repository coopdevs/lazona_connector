from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
import httpretty
import os


class DeliveryViewTests(TestCase):

    def setUp(self):
        os.environ['KOIKI_HOST'] = 'https://testing_host'

        self.url = reverse('deliveries:create')
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
        self.api_url = 'https://testing_host/rekis/api/altaEnvios'

        self.user = User.objects.create_superuser('admin', 'admin@example.com', 'pass')

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_successful_request(self):
        httpretty.register_uri(httpretty.POST, self.api_url, status=200, content_type='text/json')

        token = Token.objects.create(key='test token', user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.post(self.url, self.data, format='json')

        self.assertEqual(response.data['order_key'], self.data['order_key'])
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
