from unittest import TestCase

from koiki.recipient import Recipient


class RecipientTest(TestCase):

    def test_to_dict(self):
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

        self.assertEqual(recipient.to_dict(), {
            'nombreDesti': shipping['first_name'],
            'apellidoDesti': shipping['last_name'],
            'direccionDesti': shipping['address_1'] + ' ' + shipping['address_2'],
            'codPostalDesti': shipping['postcode'],
            'poblacionDesti': shipping['city'],
            'provinciaDesti': shipping['state'],
            'paisDesti': shipping['country'],

            'telefonoDesti': billing['phone'],
            'emailDesti': billing['email']
        })

    def test_to_dict_without_address_2(self):
        shipping = {
            'first_name': 'Philip',
            'last_name': 'Glass',
            'address_1': 'Pl. de la Vila',
            'address_2': '',
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

        self.assertEqual(recipient.to_dict(), {
            'nombreDesti': shipping['first_name'],
            'apellidoDesti': shipping['last_name'],
            'direccionDesti': shipping['address_1'],
            'codPostalDesti': shipping['postcode'],
            'poblacionDesti': shipping['city'],
            'provinciaDesti': shipping['state'],
            'paisDesti': shipping['country'],

            'telefonoDesti': billing['phone'],
            'emailDesti': billing['email']
        })
