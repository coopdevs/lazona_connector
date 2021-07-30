import httpretty
import json

from django.urls import reverse
from django.contrib.admin.sites import AdminSite
from django.test import TestCase
from django.test import RequestFactory
from api.models import Shipment, ShipmentStatus
from api.admin import ShipmentAdmin
import lazona_connector.vars


class MockSuperUser:
    def has_perm(self, perm):
        return True


request_factory = RequestFactory()
request = request_factory.get("/admin")
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

        httpretty.register_uri(
            httpretty.GET,
            f"{lazona_connector.vars.wcfmmp_host}/wp-json/wcfmmp/v1/settings/id/5",
            status=200,
            content_type="application/json",
            body=json.dumps(
                {
                    "phone": "",
                    "address": {
                        "street_1": "",
                        "street_2": "",
                        "city": "",
                        "zip": "",
                        "country": "ES",
                        "state": "",
                    },
                }
            ),
        )
        httpretty.register_uri(
            httpretty.GET,
            f"{lazona_connector.vars.wp_host}/wp-json/wp/v2/users/5?context=edit",
            status=200,
            content_type="application/json",
            body=json.dumps(
                {
                    "id": 5,
                    "username": "Queviure",
                    "email": "test@taronges.es",
                    "roles": ["testrole"],
                }
            ),
        )
        httpretty.register_uri(
            httpretty.POST,
            f"{lazona_connector.vars.koiki_host}/rekis/api/altaEnvios",
            status=200,
            content_type="text/json",
            body=json.dumps(
                {
                    "respuesta": "101",
                    "envios": [
                        {
                            "respuesta": "101",
                            "numPedido": "abc",
                            "etiqueta": "ZXRpcXVldGE=",
                            "codBarras": "123",
                        }
                    ],
                }
            ),
        )

    def test_shipment_actions(self):
        actions = self.admin.shipment_actions(self.shipment)
        self.assertEqual(
            actions,
            '<a class="button" href="/admin/api/shipment/{}'.format(self.shipment.id)
            + '/delivery/retry/">Reintentar enviament</a>'
            + '<a class="button" href="/admin/api/shipment/{}'.format(self.shipment.id)
            + "/delivery/update-status/\">Actualitzar estat de l'enviament</a>",
        )

    def test_retry_delivery(self):
        httpretty.register_uri(
            httpretty.GET,
            f"{lazona_connector.vars.wcfmmp_host}/wp-json/wc/v3/orders/2",
            status=200,
            content_type="application/json",
            body=json.dumps(
                {
                    "id": 2,
                    "order_key": "xxx",
                    "customer_note": "",
                    "shipping": {
                        "first_name": "John",
                        "last_name": "Lennon",
                        "address_1": "Beatles Street 66",
                        "address_2": "",
                        "postcode": "08032",
                        "city": "Barcelona",
                        "state": "Barcelona",
                        "country": "ES",
                    },
                    "billing": {"phone": "666666666", "email": "lennon@example.com"},
                    "line_items": [
                        {
                            "id": 17,
                            "quantity": 1,
                            "name": "Suc Taronja 1l",
                            "meta_data": [
                                {
                                    "id": 172,
                                    "key": "_vendor_id",
                                    "value": "5",
                                    "display_key": "Store",
                                    "display_value": "Tenda Taronja",
                                }
                            ],
                        },
                        {
                            "id": 11,
                            "quantity": 2,
                            "name": "Suc Poma 1l",
                            "meta_data": [
                                {
                                    "id": 179,
                                    "key": "_vendor_id",
                                    "value": "9",
                                    "display_key": "Store",
                                    "display_value": "Tenda Poma",
                                }
                            ],
                        },
                    ],
                }
            ),
        )
        previous_time = self.shipment.updated_at
        response = self.admin.retry_delivery(request, self.shipment.id)
        expected_url = reverse("admin:api_shipment_change", args=(self.shipment.id,))
        self.assertRedirects(
            response,
            expected_url,
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=False,
        )
        self.shipment.refresh_from_db()
        self.assertGreater(self.shipment.updated_at, previous_time)
        self.assertEqual(self.shipment.delivery_id, "123")
        self.assertEqual(self.shipment.status, ShipmentStatus.LABEL_SENT)

    def test_retry_delivery_wrong_order(self):
        httpretty.register_uri(
            httpretty.GET,
            f"{lazona_connector.vars.wcfmmp_host}/wp-json/wc/v3/orders/2",
            status=200,
            content_type="application/json",
            body=json.dumps({"id": 2}),
        )
        previous_time = self.shipment.updated_at
        response = self.admin.retry_delivery(request, self.shipment.pk)
        self.shipment.refresh_from_db()
        self.assertEqual(self.shipment.updated_at, previous_time)
        self.assertEqual(response.status_code, 400)

    # def test_update_delivery_status(self):
    #     response = self.admin.update_delivery_status(request, self.shipment.pk)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(
    #         response.content,
    #         bytes("updating delivery status of {}".format(self.shipment.pk), response.charset)
    #     )
