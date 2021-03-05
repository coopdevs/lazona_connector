from django.test import TestCase

from koiki.delivery import Delivery


class DeliveryTests(TestCase):

    def test_attributes(self):
        data = {'numPedido': '456_xxx', 'codBarras': 'JJD00026901003806220001', 'etiqueta': 'abc'}

        delivery = Delivery(data)

        self.assertEqual(
            delivery.to_dict(),
            {'number': '456_xxx', 'barcode': 'JJD00026901003806220001', 'label': 'abc'}
        )
