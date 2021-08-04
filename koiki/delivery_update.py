from lazona_connector.vars import koiki_tracking_host, koiki_tracking_auth_token


class UpdateDelivery():

    def __init__(self, delivery_id):
        self.delivery_id = delivery_id

    def body(self):
        return {
            'code': self.delivery_id
        }

    def auth_body(self):
        return {**self.body(), **{"token": koiki_tracking_auth_token}}

    def url(self):
        return f'{koiki_tracking_host}/kis/api/v1/service/track/see'
