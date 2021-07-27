from rest_framework import status
import requests
import json
import copy

from koiki.delivery_create import CreateDelivery
from koiki.delivery_update import UpdateDelivery
from koiki.delivery import Delivery
from koiki.order import Order
import koiki.vars

# API_PATH = "/rekis/api"


class Client:
    def __init__(self, auth_token=koiki.vars.auth_token, logger=koiki.vars.logger):
        self.auth_token = auth_token
        self.host = koiki.vars.host
        self.logger = logger

    def create_delivery(self,order_data):
        order = Order(order_data)
        endpoint_req = CreateDelivery(order)
        req_body = self._authentication(endpoint_req)
        url = self._url(endpoint_req)
        self.logger.debug('Koiki request to {}. body={}'.format(url, req_body))

        response = requests.post(url, json=req_body)
        response_body = json.loads(response.text)

        deliveries = []
        if response.status_code == status.HTTP_200_OK:
            for num, delivery_data in enumerate(response_body["envios"]):
                vendor = order.vendors[num]
                req_body_shipping = req_body["envios"][num]
                delivery_data["order_id"] = order.order_id
                delivery = Delivery(delivery_data, vendor, req_body_shipping)

                if delivery._is_errored():
                    self._log(delivery.get_data_val("response"), delivery.data, level="error")
                else:
                    self._log(delivery.get_data_val("response"), self._masked_body(delivery_data))

                deliveries.append(delivery)

        else:
            self._log(response.status_code, response_body, level="error")

        return deliveries

    def update_delivery_status(self,delivery_id):
        endpoint_req = UpdateDelivery(delivery_id)
        req_body = self._authentication(endpoint_req)
        url = self._url(endpoint_req)
        self.logger.debug('Koiki request to {}. body={}'.format(url, req_body))

        response = requests.post(url, json=req_body)
        response_body = json.loads(response.text)

        return response

    def _url(self, endpoint_req):
        return f"{self.host}{endpoint_req.url()}"

    def _authentication(self, endpoint_req):
        return {**endpoint_req.body(), **{"token": self.auth_token}}

    # So far we've seen that failed responses come as:
    #
    #   {"respuesta":"102","mensaje":"ERROR IN THE RECEIVED DATA",...}
    #
    # while successful ones as:
    #
    #   {"respuesta":"101","mensaje":"OK",...}
    #

    def _log(self, code, msg, level="info"):
        log_line = "Koiki response. status={}, body={}".format(code, msg)

        if level == "info":
            self.logger.info(log_line)
        else:
            self.logger.error(log_line)

    def _masked_body(self, data):
        masked_body = copy.deepcopy(data)
        masked_body["etiqueta"] = f"{masked_body['etiqueta'][:10]}..."
        return masked_body
