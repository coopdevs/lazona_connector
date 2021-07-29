from rest_framework import status
import requests
import json
import copy

from koiki.delivery_create import CreateDelivery
from koiki.delivery_update import UpdateDelivery
from koiki.delivery_status import DeliveryStatus
from koiki.delivery import Delivery
from koiki.order import Order
import lazona_connector.vars

# API_PATH = "/rekis/api"


class Client:
    def __init__(
        self,
        logger=lazona_connector.vars.logger
    ):
        self.logger = logger

    def create_delivery(self, order_data, vendor_id=None):
        order = Order(order_data).filter_by_vendor(vendor_id)
        create_delivery = CreateDelivery(order)
        req_body_create_delivery = create_delivery.body()
        self.logger.debug(
            'Koiki request to {}. body={}'.format(
                create_delivery.url(),
                create_delivery.body()
            )
        )

        response = requests.post(
            create_delivery.url(),
            json=create_delivery.auth_body())
        response_body = json.loads(response.text)

        deliveries = []
        if response.status_code == status.HTTP_200_OK:
            for num, delivery_data in enumerate(response_body["envios"]):
                vendor = order.vendors[num]
                req_body_shipping = req_body_create_delivery["envios"][num]
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

    def update_delivery_status(self, delivery_id):
        update_delivery = UpdateDelivery(delivery_id)
        self.logger.debug(
            'Koiki request to {}. body={}'.format(
                update_delivery.url(),
                update_delivery.body()
            )
        )
        response = requests.post(
            update_delivery.url(),
            json=update_delivery.auth_body()
        )
        if response.status_code == status.HTTP_200_OK:
            response_body = json.loads(response.text)
            DeliveryStatus(response_body)
            # status_code = delivery_status.get_data_val('status_code')
            return True
        return False

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
