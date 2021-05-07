from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from unittest.mock import patch, MagicMock
import httpretty
import json

import koiki
from koiki.error import Error


class DeliveryViewTests(TestCase):

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True

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
        self.api_url = 'https://testing_host/rekis/api/altaEnvios'

        self.user = User.objects.create_superuser('admin', 'admin@example.com', 'pass')

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_successful_request(self):
        httpretty.register_uri(
                httpretty.GET,
                f'{koiki.wcfmmp_host}/wp-json/wcfmmp/v1/settings/id/6',
                status=200,
                content_type='application/json',
                body=json.dumps({
                    "store_email": "queviure@lazona.coop",
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
        )
        httpretty.register_uri(
                httpretty.POST, self.api_url, status=200, content_type='text/json',
                body=json.dumps({
                    'respuesta': '101',
                    'envios': [{
                        'numPedido': 'abc',
                        'etiqueta': 'ZXRpcXVldGE=',
                        'codBarras': '123'
                    }]
                })
        )

        token = Token.objects.create(key='test token', user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.post(self.url, self.data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_invalid_request(self):
        response = self.client.post(self.url, {})

        self.assertEqual(response.data['order_key'][0].code, 'required')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('api.views.Client', autospec=True)
    def test_unsuccessful_request(self, mock_client):
        client = MagicMock()
        client.create_delivery.return_value = Error({'mensaje': 'ERROR IN THE RECEIVED DATA'})
        mock_client.return_value = client

        token = Token.objects.create(key='test token', user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        response = self.client.post(self.url, self.data, format='json')

        self.assertEqual(response.data, {'error': 'ERROR IN THE RECEIVED DATA'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_request(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(self.url, {})

        self.assertEqual(response.content,
                         b'{"detail":"Authentication credentials were not provided."}')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('api.views.Client', autospec=True)
    def test_pdf_persistance(self, mock_client):
        mock_delivery = MagicMock(name='delivery')
        client = MagicMock(name='client')
        client.create_delivery.return_value = mock_delivery
        mock_delivery.print_pdf.return_value = MagicMock()

        mock_client.return_value = client

        token = Token.objects.create(key='test token', user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.client.post(self.url, self.data, format='json')

        mock_delivery.print_pdf.assert_called_once()
