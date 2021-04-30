from unittest import TestCase
from unittest.mock import patch, MagicMock
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
        self.assertEquals(line_item.vendor, Vendor('5', 'A granel'))

    def test_line_item_without_vendor(self):
        data = {
            'id': 1,
            'quantity': 1,
            'meta_data': []
        }
        self.assertRaises(Exception, LineItem, data)

    def test_vendor(self):
        vendor = Vendor(1, 'name')

        self.assertEquals(vendor.id, 1)
        self.assertEquals(vendor.name, 'name')

    @patch('koiki.woocommerce.models.logging', autospec=True)
    def test_vendor_get(self, mock_logger):
        httpretty.register_uri(
            httpretty.GET,
            'http://staging.lazona.coop/wp-json/wcfmmp/v1/settings/id/1',
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

        mock_logger = MagicMock()
        vendor = Vendor(1, 'name', logger=mock_logger)
        vendor.get()

        self.assertEquals(vendor.address, "Passeig de Gràcia 1")
        self.assertEquals(vendor.zip, "08092")

        mock_logger.info.assert_called_once_with(
            'Wcfmpp request. url=http://staging.lazona.coop/wp-json/wcfmmp/v1/settings/id/1')

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
