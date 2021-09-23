from collections import defaultdict
from koiki.woocommerce.resources import LineItem, ShippingLine


class Order():

    def __init__(self, data):
        self.data = data
        self.order_id = data['id']
        self.number = data['order_key']
        self.note = data.get('customer_note', '')
        self.vendors = []
        self.by_vendor = self._by_vendor(data['line_items'])
        self.by_method = self._by_method(data['shipping_lines'])

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
        by_vendor = defaultdict(list)
        vendors = []

        for line_item in line_items:
            item = LineItem(line_item)
            by_vendor[item.vendor.id].append(item)
            vendors.append(item.vendor)
        self.vendors = vendors

        return by_vendor

    def filter_by_vendor(self, vendor_id):
        if vendor_id:
            self.by_vendor = {vendor_id: self.by_vendor[vendor_id]}

        for vendor in self.vendors:
            if vendor.id == vendor_id:
                self.vendors = [vendor]
                break

        return self

    def _by_method(self, shipping_lines):
        by_method = defaultdict(list)
        for line_item in shipping_lines:
            item = ShippingLine(line_item)
            by_method[item.method_id].append(item.vendor.id)

        return by_method

    def filter_by_method(self, method_id):
        method_mapping = {"KOIKI": "wcfmmp_product_shipping_by_zone",
                          "LOCAL_PICKUP": "local_pickup"}

        method_vendors = self.by_method[method_mapping[method_id]]
        by_vendor_method = {}
        for vendor_id in method_vendors:
            by_vendor_method[vendor_id] = self.by_vendor[vendor_id]
        self.by_vendor = by_vendor_method

        filtered_vendors = []
        for vendor in self.vendors:
            if vendor.id in method_vendors:
                filtered_vendors.append(vendor)
        self.vendors = filtered_vendors

        return self


class LocalPickupOrder(Order):
    def __init__(self, data):
        super().__init__(data)
        self = self.filter_by_method(ShipmentMethod.LOCAL_PICKUP)
