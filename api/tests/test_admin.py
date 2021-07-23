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


class MockSuperUserTest(TestCase):

    def test_admin_user_permissions(self):
        self.assertTrue(request.user.has_perm("any_perrmission_you_could_need"))


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

    def test_shipment_actions(self):
        actions = self.admin.shipment_actions(self.shipment)
        self.assertEqual(
            actions,
            '<a class="button" href="/admin/api/shipment/{}'.format(self.shipment.pk) +
            '/delivery/retry/">Reintentar enviament</a>'
        )

    def test_retry_delivery(self):
        response = self.admin.retry_delivery(request, self.shipment.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content,
            bytes("retrying delivery of {}".format(self.shipment.pk), response.charset)
        )
