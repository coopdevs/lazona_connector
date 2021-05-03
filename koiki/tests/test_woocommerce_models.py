from unittest import TestCase
from unittest.mock import patch
import httpretty
import json

from koiki.woocommerce.models import LineItem, Vendor, Shipping, Billing


class WooocommerceModelsTest(TestCase):

    def test_line_item(self):
        metadata = [
            {
                'id': 234,
                'key': '_dummy_id',
                'value': '2',
                'display_key': 'Dummy key',
                'display_value': 'Dummy value'
            },
            {
                'id': 123,
                'key': '_vendor_id',
                'value': '5',
                'display_key': 'Store',
                'display_value': 'A granel'
            }
        ]
        line_item = {
            'quantity': 3,
            'meta_data': metadata
        }

        line_item = LineItem(line_item)

        self.assertEquals(line_item.quantity, 3)
        self.assertEquals(line_item.vendor, Vendor(id='5', name='A granel'))

    def test_line_item_without_vendor(self):
        data = {
            'id': 1,
            'quantity': 1,
            'meta_data': []
        }
        self.assertRaises(Exception, LineItem, data)

    def test_vendor(self):
        vendor = Vendor(id=1, name='name')

        self.assertEquals(vendor.id, 1)
        self.assertEquals(vendor.name, 'name')

    def test_vendor_get(self):
        httpretty.register_uri(
            httpretty.GET,
            'https://wcfmmp_testing_host/wp-json/wcfmmp/v1/settings/id/1',
            status=200,
            content_type='application/json',
            body=json.dumps({
                "store_email": "store@example.com",
                "phone": "+34666554433",
                "address": {
                    "street_1": "Passeig de Gràcia 1",
                    "street_2": "",
                    "city": "Barcelona",
                    "zip": "08092",
                    "country": "ES",
                    "state": "Barcelona"
                }
            })
        )

        vendor = Vendor(id=1, name='name')
        vendor.get()

        self.assertEquals(vendor.address, "Passeig de Gràcia 1")
        self.assertEquals(vendor.zip, "08092")

    def test_shipping(self):
        data = {
            'first_name': 'Philip',
            'last_name': 'Glass',
            'address_1': 'Pl. de la Vila',
            'address_2': '1 3',
            'postcode': '08921',
            'city': 'Santa Coloma de Gramenet',
            'state': 'Barcelona',
            'country': 'Catalunya'
        }
        shipping = Shipping(data)

        self.assertEquals(shipping.first_name, 'Philip')

    def test_billing_with_country_code(self):
        data = {
            'email': 'email@example.com',
            'phone': '+34666554433'
        }
        billing = Billing(data)

        self.assertEquals(billing.phone, '666554433')

    def test_billing_without_country_code(self):
        data = {
            'email': 'email@example.com',
            'phone': '666554433'
        }
        billing = Billing(data)

        self.assertEquals(billing.phone, '666554433')
