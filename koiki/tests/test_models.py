from unittest import TestCase
from koiki.resources import Shipment, Sender, Recipient
from koiki.woocommerce.resources import Vendor, Billing, Shipping


class ModelsTest(TestCase):

    maxDiff = None

    def setUp(self):
        self.order = {"order_key": 123, "customer_note": "nota"}

    def test_shipment(self):
        shipment = Shipment(self.order, packages=2)

        self.assertDictEqual(
            shipment.to_dict(),
            {
                "numPedido": 123,
                "observaciones": "nota",
                "tipoServicio": "",
                "reembolso": 0.0,
                "kilos": 0.0,
                # TODO: Refactor we're forcing each vendor generates always 1 package.
                "bultos": 1,
            },
        )

    def test_shipment_default_packages(self):
        shipment = Shipment(self.order)

        self.assertDictEqual(
            shipment.to_dict(),
            {
                "numPedido": 123,
                "observaciones": "nota",
                "tipoServicio": "",
                "reembolso": 0.0,
                "kilos": 0.0,
                "bultos": 1,
            },
        )

    def test_sender(self):
        vendor = Vendor(
            id=1,
            name="Quèviure",
            address="C/ queviure, 1",
            zip="08080",
            email="queviure@lazona.coop",
            country="ES",
            city="Barcelona",
            state="B",
            phone="+34666554433",
        )
        sender = Sender(vendor)

        self.assertDictEqual(
            sender.to_dict(),
            {
                "nombreRemi": "Quèviure",
                "apellidoRemi": "",
                "direccionRemi": "C/ queviure, 1",
                "numeroCalleRemi": "",
                "codPostalRemi": "08080",
                "poblacionRemi": "Barcelona",
                "provinciaRemi": "Barcelona",
                "paisRemi": "ES",
                "emailRemi": "queviure@lazona.coop",
                "telefonoRemi": "+34666554433",
            },
        )

    def test_recipient(self):
        shipping = Shipping(
            {
                "first_name": "Philip",
                "last_name": "Glass",
                "address_1": "Pl. de la Vila",
                "address_2": "1 3",
                "postcode": "08921",
                "city": "Santa Coloma de Gramenet",
                "state": "Barcelona",
                "country": "ES",
            }
        )
        billing = Billing({"email": "email@example.com", "phone": "+34666554433"})

        recipient = Recipient(shipping, billing)

        self.assertDictContainsSubset(
            {
                "nombreDesti": shipping.first_name,
                "apellidoDesti": shipping.last_name,
                "direccionDesti": shipping.address_1,
                "direccionAdicionalDesti": shipping.address_2,
                "numeroCalleDesti": "",
                "codPostalDesti": shipping.postcode,
                "poblacionDesti": shipping.city,
                "provinciaDesti": shipping.state,
                "paisDesti": shipping.country,
            },
            recipient.to_dict(),
        )

        self.assertDictContainsSubset(
            {"telefonoDesti": billing.phone, "emailDesti": billing.email}, recipient.to_dict()
        )
