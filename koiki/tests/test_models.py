from unittest import TestCase

from koiki.models import Shipment, Sender, Recipient
from koiki.woocommerce.models import Vendor


class ModelsTest(TestCase):

    maxDiff = None

    def setUp(self):
        self.order = {
            'order_key': 123,
            'customer_note': 'nota'
        }

    def test_shipment(self):
        shipment = Shipment(self.order, packages=2)

        self.assertDictEqual(shipment.to_dict(), {
            'numPedido': 123,
            'observaciones': 'nota',
            'tipoServicio': '',
            'reembolso': 0.0,
            'kilos': 0.0,
            'bultos': 2
        })

    def test_shipment_default_packages(self):
        shipment = Shipment(self.order)

        self.assertDictEqual(shipment.to_dict(), {
            'numPedido': 123,
            'observaciones': 'nota',
            'tipoServicio': '',
            'reembolso': 0.0,
            'kilos': 0.0,
            'bultos': 1
        })

    def test_sender(self):
        vendor = Vendor(id=1, name='Quèviure')
        sender = Sender(vendor)

        self.assertDictEqual(sender.to_dict(), {
            'nombreRemi': 'Quèviure',
            'apellidoRemi': '',
            'direccionRemi': 'C/ La Zona, 1',
            'numeroCalleRemi': '',
            'codPostalRemi': '08186',
            'poblacionRemi': 'Barcelona',
            'provinciaRemi': 'Barcelona',
            'paisRemi': 'ES',
            'emailRemi': 'lazona@opcions.org',
            'telefonoRemi': '518888191',
        })

    def test_recipient(self):
        shipping = {
            'first_name': 'Philip',
            'last_name': 'Glass',
            'address_1': 'Pl. de la Vila',
            'address_2': '1 3',
            'postcode': '08921',
            'city': 'Santa Coloma de Gramenet',
            'state': 'Barcelona',
            'country': 'Catalunya'
        }
        billing = {
            'email': 'email@example.com',
            'phone': '+34666554433'
        }
        order = {'shipping': shipping, 'billing': billing}

        recipient = Recipient(order)

        self.assertDictEqual(recipient.to_dict(), {
            'nombreDesti': shipping['first_name'],
            'apellidoDesti': shipping['last_name'],
            'direccionDesti': shipping['address_1'],
            'direccionAdicionalDesti': shipping['address_2'],
            'numeroCalleDesti': '',
            'codPostalDesti': shipping['postcode'],
            'poblacionDesti': shipping['city'],
            'provinciaDesti': shipping['state'],
            'paisDesti': shipping['country'],

            'telefonoDesti': billing['phone'],
            'emailDesti': billing['email']
        })