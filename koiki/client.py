import requests
import json
import copy

from koiki.create_delivery import CreateDelivery
from koiki.delivery import Delivery
from koiki.order import Order

import koiki

API_PATH = '/rekis/api'


class Client():

    def __init__(self, order, auth_token=koiki.auth_token, logger=koiki.logger):
        self.order = Order(order)
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

        deliveries = []
        for num, delivery_data in enumerate(response_body['envios']):
            vendor = self.order.vendors[num]
            delivery_data['wc_order_id'] = self.order.data['order_key']
            delivery = Delivery(delivery_data, vendor)
            if delivery._is_errored():
                self._log(delivery.data.get('respuesta'), delivery.data, level='error')
            else:
                self._log(delivery.data.get('respuesta'), self._masked_body(delivery_data))

            deliveries.append(delivery)

        return deliveries

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

    def _log(self, code, msg, level='info'):
        log_line = "Koiki response. status={}, body={}".format(code, msg)

        if level == 'info':
            self.logger.info(log_line)
        else:
            self.logger.error(log_line)

    def _masked_body(self, data):
        masked_body = copy.deepcopy(data)
        masked_body['etiqueta'] = f"{masked_body['etiqueta'][:10]}..."
        return masked_body
