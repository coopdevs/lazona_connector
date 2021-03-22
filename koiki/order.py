class Order():

    def __init__(self, order):
        self.number = order['order_key']
        self.note = order.get('customer_note', '')

    def to_dict(self):
        return {
            'numPedido': self.number,
            'bultos': 1,
            'kilos': 1.0,
            'tipoServicio': '',
            'reembolso': 0.0,
            'observaciones': self.note
        }
