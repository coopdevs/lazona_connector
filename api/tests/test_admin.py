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

    def test_shipment_actions_with_errored_shipment(self):
        self.shipment.status = ShipmentStatus.ERROR_FROM_BODY
        actions = self.admin.shipment_actions(self.shipment)
        self.assertEqual(
            actions,
            '<a class="button" href="javascript: '
            + "window.location.href = '/admin/api/shipment/{}/delivery/retry/'\">".format(
                self.shipment.id
            )
            + "Reintentar enviament</a>"
            + ' <a class="button" href="/admin/api/shipment/{}'.format(self.shipment.id)
            + "/delivery/update-status/\">Actualitzar estat de l'enviament</a>",
        )

    def test_shipment_actions_with_confirm_shipment_already_sent(self):
        self.shipment.status = ShipmentStatus.LABEL_SENT
        actions = self.admin.shipment_actions(self.shipment)
        self.assertIn("confirm(", actions)

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
                    "shipping_lines": [
                        {
                            "id": 54,
                            "method_title": "Enviament Koiki",
                            "method_id": "wcfmmp_product_shipping_by_zone",
                            "meta_data": [{
                                "id": 172,
                                "key": "vendor_id",
                                "value": "5",
                                "display_key": "Store",
                                "display_value": "Tenda Taronja",
                            }]
                        }
                    ],
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

    def test_update_delivery_status_wrong_delivery_id(self):
        self.shipment.delivery_id = ""
        self.shipment.save()
        response = self.admin.update_delivery_status(request, self.shipment.id)
        self.assertEqual(response.status_code, 400)

    def test_update_delivery_status_wrong_api_response(self):
        httpretty.register_uri(
            httpretty.POST,
            f"{lazona_connector.vars.koiki_tracking_host}/kis/api/v1/service/track/see",
            status=500,
            content_type="text/json",
            body=json.dumps({}),
        )

        response = self.admin.update_delivery_status(request, self.shipment.id)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b"La crida a la API no s'ha realitzat correctament")

    def test_update_delivery_status_success(self):
        httpretty.register_uri(
            httpretty.POST,
            f"{lazona_connector.vars.koiki_tracking_host}/kis/api/v1/service/track/see",
            status=200,
            content_type="text/json",
            body=json.dumps(
                {
                    "result": [
                        {
                            "servicio": "JJD00026901005395958001",
                            "codEstado": "Envío entregado",
                            "date": "2021-07-26T09:49:37+0000",
                            "code": 108,
                        },
                        {
                            "servicio": "JJD00026901005395958001",
                            "codEstado": "Envio en Reparto",
                            "date": "2021-07-26T07:09:21+0000",
                            "code": 901,
                        },
                    ]
                }
            ),
        )

        response = self.admin.update_delivery_status(request, self.shipment.id)
        expected_url = reverse("admin:api_shipment_change", args=(self.shipment.id,))
        self.assertRedirects(
            response,
            expected_url,
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=False,
        )
