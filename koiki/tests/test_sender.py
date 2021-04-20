from unittest import TestCase

from koiki.sender import Sender


class SenderTest(TestCase):

    def test_to_dict(self):
        sender = Sender()

        self.assertEqual(sender.to_dict(), {
            'nombreRemi': 'La Zona',
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
