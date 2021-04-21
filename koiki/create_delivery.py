from koiki.sender import Sender
from koiki.recipient import Recipient
from koiki.shipment import Shipment
from koiki.line_item import LineItem


class CreateDelivery():
    LABEL_FORMAT = 'PDF'
    RESOURCE_PATH = '/altaEnvios'

    def __init__(self, order):
        self.order = order
        self.recipient = Recipient(order)
        self.line_items = order['line_items']
        self.by_vendor = self._by_vendor()

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

        for vendor_id in self.by_vendor.keys():
            line_items = self.by_vendor[vendor_id]
            vendor = line_items[0].vendor

            deliveries.append(self._delivery(line_items, vendor))

        return deliveries

    def _by_vendor(self):
        by_vendor = {}

        for line_item in self.line_items:
            item = LineItem(line_item)
            vendor_id = item.vendor.id

            if vendor_id in by_vendor.keys():
                by_vendor[vendor_id].append(item)
            else:
                by_vendor[vendor_id] = [item]

        return by_vendor

    # A vendor delivery consists of a Sender (which maps to a marketplace vendor) and a Recipient
    #
    # Builds a delivery structure from all the line_items, which are sold by the same vendor
    def _delivery(self, line_items, vendor):
        total_quantity = 0

        for line_item in line_items:
            total_quantity += line_item.quantity

        return {
            **Shipment(self.order, packages=total_quantity).to_dict(),
            **self.recipient.to_dict(),
            **Sender(vendor).to_dict(),
        }
