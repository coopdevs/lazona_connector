from collections import defaultdict

from koiki.models import Sender, Recipient, Shipment
from koiki.woocommerce.models import LineItem, Shipping, Billing


class CreateDelivery():
    LABEL_FORMAT = 'PDF'
    RESOURCE_PATH = '/altaEnvios'

    def __init__(self, order):
        self.order = order
        self.by_vendor = self._by_vendor(order['line_items'])
        self.shipping = Shipping(order['shipping'])
        self.billing = Billing(order['billing'])

    def body(self):
        return {
            'formatoEtiqueta': self.LABEL_FORMAT,
            'envios': self._deliveries()
        }

    def url(self):
        return self.RESOURCE_PATH

    # Builds a single delivery for each vendor, aggregating the line items that vendor sold
    def _deliveries(self):
        deliveries = []

        for vendor_id, line_items in self.by_vendor.items():
            vendor = line_items[0].vendor
            deliveries.append(self._delivery(line_items, vendor))

        return deliveries

    def _by_vendor(self, line_items):
        by_vendor = defaultdict(list)

        for line_item in line_items:
            item = LineItem(line_item)
            by_vendor[item.vendor.id].append(item)

        return by_vendor

    # Builds a delivery structure from all passed line_items, which are provided by the same vendor
    def _delivery(self, line_items, vendor):
        total_quantity = 0
        vendor.fetch()

        for line_item in line_items:
            total_quantity += line_item.quantity

        return {
            **Shipment(self.order, packages=total_quantity).to_dict(),
            **Recipient(self.shipping, self.billing).to_dict(),
            **Sender(vendor).to_dict(),
        }
