class Delivery():

    def __init__(self, data):
        self.data = data

    def to_dict(self):
        return {
            'number': self.data['numPedido'],
            'barcode': self.data['codBarras'],
            'label': self.data['etiqueta']
        }
