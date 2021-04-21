from unittest import TestCase

from koiki.sender import Sender
from koiki.vendor import Vendor


class SenderTest(TestCase):

    def test_to_dict(self):
        vendor = Vendor(id=1, name='Quèviure')
        sender = Sender(vendor)

        self.assertEqual(sender.to_dict(), {
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
