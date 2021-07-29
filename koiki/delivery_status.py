class DeliveryStatus():

    def __init__(self, response_body={}):
        self.response_body = response_body

    def to_dict(self):
        return {
            "status_txt": self._get_current_val('codEstado'),
            "status_code": self._get_current_val('codEstado'),
            "status_date": self._get_current_val('codEstado'),
        }

    def _get_current_val(self, key):
        return "test"

    def get_data_val(self, key):
        return self.to_dict()[key]
