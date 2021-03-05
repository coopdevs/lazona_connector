import requests
import logging
import os
import json

from koiki.create_delivery import CreateDelivery
from koiki.delivery import Delivery
from koiki.error import Error

HOST = os.getenv('KOIKI_HOST', 'https://testing_host')
API_PATH = '/rekis/api'


class Client():

    def __init__(self, order, auth_token=os.getenv('KOIKI_AUTH_TOKEN'),
                 logger=logging.getLogger('django.server')):
        self.order = order
        self.auth_token = auth_token
        self.logger = logger

    def create_delivery(self):
        endpoint_req = CreateDelivery(self.order)
        body = self._authentication(endpoint_req)

        self.logger.info('Koiki request. body=%s', body)

        response = requests.post(self._url(endpoint_req), json=body)
        response_body = json.loads(response.text)

        if self._is_errored(response_body):
            self._log_error(response.status_code, response.text)
            return Error(response_body)
        else:
            self.logger.info(
                'Koiki response. status=%s, body=%', response.status_code, response.text)
            return Delivery(response_body['envios'][0])

    def _url(self, endpoint_req):
        return f'{HOST}{API_PATH}{endpoint_req.url()}'

    def _authentication(self, endpoint_req):
        return {**endpoint_req.body(), **{'token': self.auth_token}}

    # So far we've seen that failed responses come as:
    #
    #   {"respuesta":"102","mensaje":"ERROR IN THE RECEIVED DATA",...}
    #
    # while successful ones as:
    #
    #   {"respuesta":"101","mensaje":"OK",...}
    #
    def _is_errored(self, response_body):
        return response_body.get('respuesta', '') != '101'

    def _log_error(self, code, msg):
        self.logger.error('Failed request. status=%s, body=%s', code, msg)
