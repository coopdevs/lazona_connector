from koiki.resources import Sender, Recipient, Shipment
from koiki.woocommerce.resources import Shipping, Billing
from lazona_connector.vars import koiki_host, koiki_auth_token


class CreateDelivery():
    LABEL_FORMAT = 'PDF'

    def __init__(self, order):
        self.order = order
        self.shipping = Shipping(order.data['shipping'])
        self.billing = Billing(order.data['billing'])

    def url(self):
        return f'{koiki_host}/rekis/api/altaEnvios'

    def body(self):
        return {
            'formatoEtiqueta': self.LABEL_FORMAT,
            'envios': self._deliveries()
        }

    def auth_body(self):
        return {**self.body(), **{"token": koiki_auth_token}}

    # Builds a single delivery for each vendor, aggregating the line items that vendor sold
    def _deliveries(self):
        deliveries = []

        for vendor_id, line_items in self.order.by_vendor.items():
            vendor = line_items[0].vendor
            deliveries.append(self._delivery(line_items, vendor))

        return deliveries

    # Builds a delivery structure from all passed line_items, which are provided by the same vendor
    def _delivery(self, line_items, vendor):
        total_quantity = 0
        vendor.fetch()

        for line_item in line_items:
            total_quantity += line_item.quantity

        return {
            **Shipment(self.order.data, packages=total_quantity).to_dict(),
            **Recipient(self.shipping, self.billing).to_dict(),
            **Sender(vendor).to_dict(),
        }
