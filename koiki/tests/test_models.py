from unittest import TestCase
from unittest.mock import MagicMock

from koiki.models import Shipment, Sender, Recipient
from koiki.woocommerce.models import Vendor, Billing, Shipping

import json


class FakeResponse():
    def __init__(self, body):
        self.body = body

    def json(self):
        if isinstance(self.body, dict):
            return self.body
        else:
            return json.loads(self.body)


class FakeClient():
    def __init__(self, resp_body):
        self.resp_body = resp_body

    def get(self, _url):
        return FakeResponse(self.resp_body)


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
        fake_client = FakeClient({
            "store_name": "Quèviure",
            "store_email": "queviure@lazona.coop",
            "phone": "",
            "address": {
                "street_1": "C/ queviure, 1",
                "street_2": "",
                "city": "Barcelona",
                "zip": "08080",
                "country": "ES",
                "state": "Barcelona"
            }
        })
        vendor = Vendor(
            id=1,
            name='Quèviure',
            address='C/ queviure, 1',
            zip='08080',
            email='queviure@lazona.coop',
            country='ES',
            city='Barcelona',
            state='Barcelona',
            phone='+34666554433',
            client=fake_client
        )
        sender = Sender(vendor)

        self.assertDictEqual(sender.to_dict(), {
            'nombreRemi': 'Quèviure',
            'apellidoRemi': '',
            'direccionRemi': 'C/ queviure, 1',
            'numeroCalleRemi': '',
            'codPostalRemi': '08080',
            'poblacionRemi': 'Barcelona',
            'provinciaRemi': 'Barcelona',
            'paisRemi': 'ES',
            'emailRemi': 'queviure@lazona.coop',
            'telefonoRemi': '+34666554433',
        })

    def test_recipient(self):
        shipping = Shipping({
            'first_name': 'Philip',
            'last_name': 'Glass',
            'address_1': 'Pl. de la Vila',
            'address_2': '1 3',
            'postcode': '08921',
            'city': 'Santa Coloma de Gramenet',
            'state': 'Barcelona',
            'country': 'Catalunya'
        })
        billing = Billing({
            'email': 'email@example.com',
            'phone': '+34666554433'
        })

        recipient = Recipient(shipping, billing)

        self.assertDictContainsSubset({
            'nombreDesti': shipping.first_name,
            'apellidoDesti': shipping.last_name,
            'direccionDesti': shipping.address_1,
            'direccionAdicionalDesti': shipping.address_2,
            'numeroCalleDesti': '',
            'codPostalDesti': shipping.postcode,
            'poblacionDesti': shipping.city,
            'provinciaDesti': shipping.state,
            'paisDesti': shipping.country,
        }, recipient.to_dict())

        self.assertDictContainsSubset({
            'telefonoDesti': billing.phone,
            'emailDesti': billing.email
        }, recipient.to_dict())
