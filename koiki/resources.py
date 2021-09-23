from koiki.woocommerce.order import Order


def clean_names_for_koiki(name):
    name = name.replace("'", " ")
    name = name.replace("ç", "c")
    name = name.replace("-", " ")
    return name


class KoikiOrder(Order):

    def __init__(self, data):
        super().__init__(data)
        self = self.filter_by_method("KOIKI")

    def to_dict(self):
        return {
            'numPedido': self.number,
            'bultos': 1,
            'kilos': 1.0,
            'tipoServicio': '',
            'reembolso': 0.0,
            'observaciones': self.note
        }


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
            'poblacionRemi': clean_names_for_koiki(self.vendor.city),
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
            'poblacionDesti': clean_names_for_koiki(self.shipping.city),
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

    # TODO: control num of packages sent by each vendor.
    """
    Right now we force 1 package per vendor
    More than one package per vendor throws an error on koiki.client create_delivery
    """
    def to_dict(self):
        return {
            'numPedido': self.number,
            # 'bultos': self.packages,
            'bultos': 1,
            'kilos': 0.0,
            'tipoServicio': '',
            'reembolso': 0.0,
            'observaciones': self.note
        }
