import base64


class Delivery():

    filename = 'label.pdf'

    def __init__(self, data):
        self.data = data

    def to_dict(self):
        return {
            'number': self.data['numPedido'],
            'barcode': self.data['codBarras'],
            'label': self.data['etiqueta']
        }

    def print_pdf(self):
        content = base64.b64decode(self.data['etiqueta'])

        pdf = open(self.filename, 'wb')
        pdf.write(content)
        pdf.close()

        return pdf
