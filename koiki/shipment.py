class Shipment():

    def __init__(self, order, packages=1):
        self.number = order['order_key']
        self.note = order.get('customer_note', '')
        self.packages = packages

    # TODO: Sum up the number of items across the vendor's line items
    # We could append here the details of the vendor so we can easily identify it.
    def to_dict(self):
        return {
            'numPedido': self.number,
            'bultos': self.packages,
            'kilos': 0.0,
            'tipoServicio': '',
            'reembolso': 0.0,
            'observaciones': self.note
        }
