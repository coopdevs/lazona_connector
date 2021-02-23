from unittest import TestCase

from koiki.recipient import Recipient


class RecipientTest(TestCase):

    def setUp(self):
        self.shipping = {
            'first_name': 'Philip',
            'last_name': 'Glass',
            'address_1': 'Pl. de la Vila',
            'address_2': '1 3',
            'postcode': '08921',
            'city': 'Santa Coloma de Gramenet',
            'state': 'Barcelona',
            'country': 'Catalunya'
        }
        self.billing = {
            'email': 'email@example.com',
            'phone': '+34666554433'
        }

    def test_to_dict(self):
        order = {'shipping': self.shipping, 'billing': self.billing}

        recipient = Recipient(order)

        self.assertEqual(recipient.to_dict(), {
            'nombreDesti': self.shipping['first_name'],
            'apellidoDesti': self.shipping['last_name'],
            'direccionDesti': self.shipping['address_1'] + ' ' + self.shipping['address_2'],
            'codPostalDesti': self.shipping['postcode'],
            'poblacionDesti': self.shipping['city'],
            'provinciaDesti': self.shipping['state'],
            'paisDesti': self.shipping['country'],

            'telefonoDesti': self.billing['phone'],
            'emailDesti': self.billing['email']
        })

    def test_to_dict_without_address_2(self):
        self.shipping['address_2'] = ''
        order = {'shipping': self.shipping, 'billing': self.billing}

        recipient = Recipient(order)

        self.assertEqual(recipient.to_dict(), {
            'nombreDesti': self.shipping['first_name'],
            'apellidoDesti': self.shipping['last_name'],
            'direccionDesti': self.shipping['address_1'],
            'codPostalDesti': self.shipping['postcode'],
            'poblacionDesti': self.shipping['city'],
            'provinciaDesti': self.shipping['state'],
            'paisDesti': self.shipping['country'],

            'telefonoDesti': self.billing['phone'],
            'emailDesti': self.billing['email']
        })
