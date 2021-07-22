from koiki.resources import Sender, Recipient, Shipment
from koiki.woocommerce.resources import Shipping, Billing


class UpdateDelivery():
    RESOURCE_PATH = '/kis/api/v1/service/track/see'

    def __init__(self, delivery_id):
        self.delivery_id = delivery_id

    def body(self):
        return {
            'code': self.delivery_id
        }

    def url(self):
        return self.RESOURCE_PATH
