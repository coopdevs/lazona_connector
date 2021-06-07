import base64

# TODO: convert this class into Django Model in order to link Koiki's shipping, with WC purchase and PDF


class Delivery():

    filename = 'label.pdf'

    def __init__(self, data, vendor):
        self.data = data
        self.vendor = vendor

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

    def send_mail_to_vendor(self):
        self.print_pdf()
        print('Sending PDF to EMAIL', self.vendor.email)
        #to send attachment with the created PDF
