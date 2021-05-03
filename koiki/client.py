import requests
import os
import json
import copy

from koiki.create_delivery import CreateDelivery
from koiki.delivery import Delivery
from koiki.error import Error

import koiki

API_PATH = '/rekis/api'


class Client():

    def __init__(self, order, auth_token=os.getenv('KOIKI_AUTH_TOKEN'), logger=koiki.logger):
        self.order = order
        self.auth_token = auth_token
        self.host = koiki.host
        self.logger = logger

    def create_delivery(self):
        endpoint_req = CreateDelivery(self.order)
        req_body = self._authentication(endpoint_req)

        url = self._url(endpoint_req)
        self.logger.info('Koiki request to {}. body={}'.format(url, req_body))

        response = requests.post(url, json=req_body)
        response_body = json.loads(response.text)

        if self._is_errored(response_body):
            self._log(response.status_code, response.text, logger='error')
            return Error(response_body)
        else:
            self._log(response.status_code, self._masked_body(response_body))
            return Delivery(response_body['envios'][0])

    def _url(self, endpoint_req):
        return f'{self.host}{API_PATH}{endpoint_req.url()}'

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

    def _log(self, code, msg, logger='info'):
        log_line = "Koiki response. status={}, body={}".format(code, msg)
        if logger == 'info':
            self.logger.info(log_line)
        else:
            self.logger.error(log_line)

    def _masked_body(self, body):
        masked_body = copy.deepcopy(body)
        for delivery in masked_body['envios']:
            delivery['etiqueta'] = f"{delivery['etiqueta'][:10]}..."
        return masked_body
