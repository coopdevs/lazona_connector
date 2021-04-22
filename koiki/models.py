class Sender():

    # Note telefonoRemi can only have 9 digits.
    def __init__(self, vendor):
        self.vendor = vendor

    def to_dict(self):
        return {
            'nombreRemi': self.vendor.name,
            'apellidoRemi': '',
            'numeroCalleRemi': '',
            'direccionRemi': 'C/ La Zona, 1',
            'codPostalRemi': '08186',
            'poblacionRemi': 'Barcelona',
            'provinciaRemi': 'Barcelona',
            'paisRemi': 'ES',
            'emailRemi': 'lazona@opcions.org',
            'telefonoRemi': '518888191',
        }


class Recipient():

    def __init__(self, order):
        self.shipping = order['shipping']
        self.billing = order['billing']

    def to_dict(self):
        return {
            'nombreDesti': self.shipping['first_name'],
            'apellidoDesti': self.shipping['last_name'],
            'direccionDesti': self.shipping['address_1'],
            'direccionAdicionalDesti': self.shipping['address_2'],
            'numeroCalleDesti': '',
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


class Shipment():

    def __init__(self, order, packages=1):
        self.number = order['order_key']
        self.note = order.get('customer_note', '')
        self.packages = packages

    def to_dict(self):
        return {
            'numPedido': self.number,
            'bultos': self.packages,
            'kilos': 0.0,
            'tipoServicio': '',
            'reembolso': 0.0,
            'observaciones': self.note
        }
