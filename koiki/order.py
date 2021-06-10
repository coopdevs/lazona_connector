from collections import defaultdict
from koiki.woocommerce.models import LineItem


class Order():

    def __init__(self, data):
        self.data = data
        self.number = data['order_key']
        self.note = data.get('customer_note', '')
        self.vendors = []
        self.by_vendor = self._by_vendor(data['line_items'])

    def to_dict(self):
        return {
            'numPedido': self.number,
            'bultos': 1,
            'kilos': 1.0,
            'tipoServicio': '',
            'reembolso': 0.0,
            'observaciones': self.note
        }

    def _by_vendor(self, line_items):
        print('line_items', line_items)
        by_vendor = defaultdict(list)
        vendors = []

        for line_item in line_items:
            item = LineItem(line_item)
            by_vendor[item.vendor.id].append(item)
            vendors.append(item.vendor)
        self.vendors = vendors

        return by_vendor
