from koiki.sender import Sender
from koiki.recipient import Recipient
from koiki.order import Order


class CreateDelivery():
    LABEL_FORMAT = 'PDF'
    RESOURCE_PATH = '/altaEnvios'

    def __init__(self, order):
        self.vendor_order = Order(order)
        self.recipient = Recipient(order)
        self.line_items = order['line_items']

    def body(self):
        return {
            'formatoEtiqueta': self.LABEL_FORMAT,
            'envios': self._deliveries()
        }

    def url(self):
        return self.RESOURCE_PATH

    def _deliveries(self):
        return [self._delivery(line_item) for line_item in self.line_items]

    # A vendor delivery consists of a Sender (which maps to a marketplace vendor) and a Recipient
    def _delivery(self, line_item):
        return {
            **self.vendor_order.to_dict(),
            **self.recipient.to_dict(),
            **Sender(line_item).to_dict(),
        }
