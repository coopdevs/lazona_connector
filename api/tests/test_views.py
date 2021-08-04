from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
import httpretty
import json
import lazona_connector.vars


class DeliveryViewTests(TestCase):

    def setUp(self):
        self.url = reverse('deliveries:create')
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
        self.api_url = f'{lazona_connector.vars.koiki_host}/rekis/api/altaEnvios'
        self.user = User.objects.create_superuser('admin', 'admin@example.com', 'pass')

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_successful_request(self):
        httpretty.register_uri(
                httpretty.GET,
                f'{lazona_connector.vars.wcfmmp_host}/wp-json/wcfmmp/v1/settings/id/6',
                status=200,
                content_type='application/json',
                body=json.dumps({
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
                httpretty.GET,
                f'{lazona_connector.vars.wp_host}/wp-json/wp/v2/users/6?context=edit',
                status=200,
                content_type='application/json',
                body=json.dumps({
                    "id": 6,
                    "username": "Queviure",
                    "email": "queviure@lazona.coop",
                    "roles": ["testrole"],
                })
        )
        httpretty.register_uri(
                httpretty.POST, self.api_url, status=200, content_type='text/json',
                body=json.dumps({
                    'respuesta': '101',
                    'envios': [{
                        'respuesta': '101',
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

    def test_unauthenticated_request(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(self.url, {})

        self.assertEqual(response.content,
                         b'{"detail":"Authentication credentials were not provided."}')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
