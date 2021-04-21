from unittest import TestCase

from koiki.line_item import LineItem
from koiki.vendor import Vendor


class LineItemTest(TestCase):

    def test(self):
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
