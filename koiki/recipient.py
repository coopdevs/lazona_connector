class Recipient():

    """Converts Woocommerce's shipping information to Koiki's recipient attributes"""

    def __init__(self, order):
        self.shipping = order['shipping']
        self.billing = order['billing']

    def to_dict(self):
        return {
            'nombreDesti': self.shipping['first_name'],
            'apellidoDesti': self.shipping['last_name'],
            'direccionDesti': self._address(),
            'codPostalDesti': self.shipping['postcode'],
            'poblacionDesti': self.shipping['city'],
            'provinciaDesti': self.shipping['state'],
            'paisDesti': self.shipping['country'],
            'telefonoDesti': self.billing['phone'],
            'emailDesti': self.billing['email']
        }

    def _address(self):
        address = self.shipping['address_1']

        if self.shipping['address_2']:
            address += ' ' + self.shipping['address_2']

        return address
