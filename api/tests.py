import json
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from unittest.mock import MagicMock

from .models import Delivery
from api.views import Client

# TODO: Move me to tests/__init__.py and make sure is still protecting us
import httpretty
httpretty.enable(allow_net_connect=False)

class DeliveryModelTests(APITestCase):

    def test_delivery(self):
        delivery = Delivery(order_number='abc')
        self.assertEqual(delivery.order_number, 'abc')

class DeliveryViewTests(TestCase):

    def test_successful_request(self):
        url = reverse('deliveries:create')
        data = {'order_number': 'xxx'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.data, {'order_number': 'xxx'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unsuccessful_request(self):
        url = reverse('deliveries:create')
        data = {}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.data, {'order_number': ['This field is required.']})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('api.views.Client', autospec=True)
    def test_koiki_client_is_used(self, mock_koiki_client):
        url = reverse('deliveries:create')
        data = {'order_number': 'xxx'}

        httpretty.register_uri(httpretty.POST, 'https://testing_host/rekis/api/altaEnvios',
                               status=200, content_type='text/json')

        response = self.client.post(url, data, format='json')

        mock_koiki_client.assert_called_once_with({
            'order_key': 'xxx',
            'shipping': {
                'first_name': 'John',
                'last_name': 'Lennon',
                'address_1': 'Beatles Street 66',
                'address_2': '',
                'postcode': '08032',
                'city': 'Barcelona',
                'state': 'Barcelona',
                'country': 'Spain'
            },
            'billing': {
                'phone': '666666666',
                'email': 'lennon@example.com'
            }
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @patch('api.views.Client.create_delivery', autospec=True)
    def test_koiki_create_delivery_is_called(self, mock_create_delivery):
        url = reverse('deliveries:create')
        data = {'order_number': 'xxx'}

        httpretty.register_uri(httpretty.POST, 'https://testing_host/rekis/api/altaEnvios',
                               status=200, content_type='text/json')

        response = self.client.post(url, data, format='json')

        mock_create_delivery.assert_called()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
