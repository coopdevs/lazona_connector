from rest_framework import status
import requests
import json
import copy

from koiki.create_delivery import CreateDelivery
from koiki.delivery import Delivery
from koiki.order import Order
from api.models import PersistentDelivery, DeliveryStatus
import koiki

API_PATH = "/rekis/api"


class Client:
    def __init__(self, order, auth_token=koiki.auth_token, logger=koiki.logger):
        self.order = Order(order)
        self.auth_token = auth_token
        self.host = koiki.host
        self.logger = logger

    def create_delivery(self):
        endpoint_req = CreateDelivery(self.order)
        req_body = self._authentication(endpoint_req)
        url = self._url(endpoint_req)
        self.logger.info("Koiki request to {}. body={}".format(url, req_body))

        response = requests.post(url, json=req_body)
        response_body = json.loads(response.text)

        deliveries = []
        if response.status_code == status.HTTP_200_OK:
            for num, delivery_data in enumerate(response_body["envios"]):
                vendor = self.order.vendors[num]
                req_body_shipping = req_body["envios"][num]
                delivery_data["order_id"] = self.order.order_id
                delivery = Delivery(delivery_data, vendor, req_body_shipping)
                delivery_pdf = None

                if delivery._is_errored():
                    self._log(delivery.data.get("respuesta"), delivery.data, level="error")
                    status_delivery = DeliveryStatus.ERROR
                else:
                    self._log(delivery.data.get("respuesta"), self._masked_body(delivery_data))
                    status_delivery = DeliveryStatus.SUCCESS
                    delivery_pdf = delivery.print_pdf()

                deliveries.append(delivery)
                PersistentDelivery(
                    shipment=delivery_data["numPedido"],
                    order=int(delivery_data["order_id"]),
                    vendor=int(vendor),
                    pdf=delivery_pdf,
                    req_body=req_body_shipping,
                    req_response=delivery_data.get("mensaje"),
                    status=status_delivery,
                )

        else:
            self._log(response.status_code, response_body, level="error")

        return deliveries

    def _url(self, endpoint_req):
        return f"{self.host}{API_PATH}{endpoint_req.url()}"

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
