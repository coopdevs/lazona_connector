from django.contrib.admin.sites import AdminSite
from django.test import TestCase
from django.test import RequestFactory
from api.models import Shipment
from api.admin import ShipmentAdmin


class MockSuperUser:
    def has_perm(self, perm):
        return True


request_factory = RequestFactory()
request = request_factory.get('/admin')
request.user = MockSuperUser()


class ShipmentAdminTest(TestCase):

    def setUp(self):
        Shipment.objects.all().delete()
        self.shipment = Shipment.objects.create(
            delivery_id="111",
            order_id=2,
            vendor_id=5,
            label_url="my_pdf_url",
            status="",
        )
        site = AdminSite()
        self.admin = ShipmentAdmin(Shipment, site)

    def test_retry_delivery(self):
        response = self.admin.retry_delivery(request, self.shipment)
        print(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content,
            bytes("retrying delivery of "+self.shipment.delivery_id, response.charset)
        )
