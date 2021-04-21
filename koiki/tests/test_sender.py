from unittest import TestCase

from koiki.sender import Sender


class SenderTest(TestCase):

    def test_to_dict(self):
        line_item = {
            'id': 1,
            'meta_data': [{
                'display_value': 'Quèviure',
                'value': '6'
            }]
        }
        sender = Sender(line_item)

        self.assertEqual(sender.to_dict(), {
            'nombreRemi': 'Quèviure',
            'apellidoRemi': '6',
            'direccionRemi': 'C/ La Zona, 1',
            'numeroCalleRemi': '',
            'codPostalRemi': '08186',
            'poblacionRemi': 'Barcelona',
            'provinciaRemi': 'Barcelona',
            'paisRemi': 'ES',
            'emailRemi': 'lazona@opcions.org',
            'telefonoRemi': '518888191',
        })
