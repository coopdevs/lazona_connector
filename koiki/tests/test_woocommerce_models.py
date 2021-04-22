from unittest import TestCase

from koiki.woocommerce.models import LineItem, Vendor


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

    def test_vendor(self):
        vendor = Vendor(1, 'name')

        self.assertEquals(vendor.id, 1)
        self.assertEquals(vendor.name, 'name')
