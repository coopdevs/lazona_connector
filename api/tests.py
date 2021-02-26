import json
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Delivery

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
