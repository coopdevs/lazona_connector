class Sender():

    # Note telefonoRemi can only have 9 digits.
    def __init__(self, vendor):
        self.vendor = vendor

    def to_dict(self):

        return {
            'nombreRemi': self.vendor.name,
            'apellidoRemi': '',
            'numeroCalleRemi': '',
            'direccionRemi': self.vendor.address,
            'codPostalRemi': self.vendor.zip,
            'poblacionRemi': self.vendor.city,
            'provinciaRemi': self.vendor.state,
            'paisRemi': self.vendor.country,
            'emailRemi': self.vendor.email,
            'telefonoRemi': self.vendor.phone,
        }


class Recipient():

    def __init__(self, shipping, billing):
        self.shipping = shipping
        self.billing = billing

    def to_dict(self):
        return {
            'nombreDesti': self.shipping.first_name,
            'apellidoDesti': self.shipping.last_name,
            'direccionDesti': self.shipping.address_1,
            'direccionAdicionalDesti': self.shipping.address_2,
            'numeroCalleDesti': '',
            'codPostalDesti': self.shipping.postcode,
            'poblacionDesti': self.shipping.city,
            'provinciaDesti': self.shipping.state,
            'paisDesti': self.shipping.country,
            'telefonoDesti': self.billing.phone,
            'emailDesti': self.billing.email
        }


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
