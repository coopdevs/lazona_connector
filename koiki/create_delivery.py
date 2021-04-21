from koiki.sender import Sender
from koiki.recipient import Recipient
from koiki.shipment import Shipment


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

        for vendor in self.by_vendor.keys():
            line_items = self.by_vendor[vendor]
            metadata = line_items[0]['meta_data']
            vendor_metadata = {}

            for datum in metadata:
                if datum['key'] == '_vendor_id':
                    vendor_metadata = datum

            deliveries.append(self._delivery(line_items, vendor_metadata))

        return deliveries

    def _by_vendor(self):
        by_vendor = {}

        for line_item in self.line_items:
            metadata = line_item['meta_data']
            vendor_id = self._vendor_id(metadata)

            if vendor_id in by_vendor.keys():
                by_vendor[vendor_id].append(line_item)
            else:
                by_vendor[vendor_id] = [line_item]

        return by_vendor

    def _vendor_id(self, metadata):
        datum = metadata[0]

        for datum in metadata:
            if datum['key'] == '_vendor_id':
                return datum['value']

        return None

    # A vendor delivery consists of a Sender (which maps to a marketplace vendor) and a Recipient
    #
    # Builds a delivery structure from all the line_items, which are sold by the same vendor
    def _delivery(self, line_items, vendor_metadata):
        delivery = {}
        total_quantity = 0

        for line_item in line_items:
            total_quantity += line_item['quantity']

        shipment = Shipment(self.order, packages=total_quantity)
        delivery = {
            **shipment.to_dict(),
            **self.recipient.to_dict(),
            **Sender(vendor_metadata).to_dict(),
        }

        return delivery
