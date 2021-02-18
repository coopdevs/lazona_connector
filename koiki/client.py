import requests

from koiki.sender import Sender
from koiki.recipient import Recipient

HOST = 'https://rekistest.koiki.es/services'
API_PATH = '/rekis/api'

class Client():
    URL = f'{HOST}{API_PATH}/altaEnvios'
    label_format = 'PDF'

    def __init__(self, order):
        self.order = order
        self.sender = Sender()
        self.recipient = Recipient(order)

    def create_delivery(self):
        response = requests.post(self.URL, json=self._body())
        return response.status_code == 200

    def _body(self):
        return {
            'formatoEtiqueta': self.label_format,
            'envios': [self._delivery()]
        }

    def _delivery(self):
        order = { 'numPedido': self.order['order_key'] }
        return {**order, **self.recipient.to_dict(), **self.sender.to_dict()}
