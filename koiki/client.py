import requests
import logging
import os
import json

from koiki.sender import Sender
from koiki.recipient import Recipient
from koiki.order import Order

HOST = os.getenv('KOIKI_HOST', 'https://testing_host')
API_PATH = '/rekis/api'


class Client():
    URL = f'{HOST}{API_PATH}/altaEnvios'
    LABEL_FORMAT = 'PDF'

    def __init__(self, order, auth_token=os.getenv('KOIKI_AUTH_TOKEN'),
                 logger=logging.getLogger('django.server')):
        self.order = Order(order)
        self.sender = Sender()
        self.recipient = Recipient(order)
        self.auth_token = auth_token
        self.logger = logger

    def create_delivery(self):
        body = self._body()
        self.logger.info('Koiki request. body=%s', body)
        response = requests.post(self.URL, json=body)

        if response.status_code != 200:
            self._log_error(response.status_code, response.text)
        elif self._errored(response):
            self._log_error(400, response.text)

        self.logger.info(
            'Koiki response. status=%s, body=%',
            response.status_code,
            response.text
        )

    def _body(self):
        return {
            'formatoEtiqueta': self.LABEL_FORMAT,
            'token': self.auth_token,
            'envios': [self._delivery()]
        }

    def _delivery(self):
        return {
            **self.order.to_dict(),
            **self.recipient.to_dict(),
            **self.sender.to_dict(),
        }

    def _errored(self, response):
        body = json.loads(response.text)
        return '102' in body.get('respuesta', '')

    def _log_error(self, code, msg):
        self.logger.error('Failed request. status=%s, body=%s', code, msg)
