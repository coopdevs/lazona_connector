from koiki.sender import Sender
from koiki.recipient import Recipient
from koiki.order import Order


class CreateDelivery():
    LABEL_FORMAT = 'PDF'
    RESOURCE_PATH = '/altaEnvios'

    def __init__(self, order):
        self.order = Order(order)
        self.recipient = Recipient(order)
        self.sender = Sender()

    def body(self):
        return {
            'formatoEtiqueta': self.LABEL_FORMAT,
            'envios': [self._delivery()]
        }

    def url(self):
        return self.RESOURCE_PATH

    def _delivery(self):
        return {
            **self.order.to_dict(),
            **self.recipient.to_dict(),
            **self.sender.to_dict(),
        }
