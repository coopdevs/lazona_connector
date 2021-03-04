import requests
import logging
import os
import json

from koiki.sender import Sender
from koiki.recipient import Recipient

HOST = os.getenv('KOIKI_HOST', 'https://testing_host')
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

        if response.status_code != 200:
            self._log_error(response.status_code, response.text)
        elif self._errored(response):
            self._log_error(400, response.text)

        logging.info(
            'Koiki response. status=%s, body=%',
            response.status_code,
            response.text
        )

    def _body(self):
        return {
            'formatoEtiqueta': self.label_format,
            'envios': [self._delivery()]
        }

    def _delivery(self):
        order = {'numPedido': self.order['order_key']}
        return {**order, **self.recipient.to_dict(), **self.sender.to_dict()}

    def _errored(self, response):
        body = json.loads(response.text)
        return '102' in body.get('respuesta', '')

    def _log_error(self, code, msg):
        logging.error('Failed request. status=%s, body=%s', code, msg)
