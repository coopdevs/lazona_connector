import os

from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth.models import User

from api.host_authentication import SignatureValidation
import rest_framework


class PayloadSignatureTests(TestCase):
    def setUp(self):
        os.environ["WC_WEBHOOK_SECRET"] = "testcase"
        self.original_payload = '{"id":6177,"parent_id":0,"status":"pending","currency":"EUR","version":"5.0.0"}'

        self.user = User(username="pau")
        self.user.save()

    def test_payload_signature_is_invalid(self):
        invalid_wc_signature = "AAAA"

        request = RequestFactory().post(
            "/path/", self.original_payload, content_type="application/json"
        )
        request.META["HTTP_X_WC_WEBHOOK_SIGNATURE"] = invalid_wc_signature
        self.assertRaises(
            rest_framework.exceptions.ValidationError,
            SignatureValidation().authenticate,
            request,
        )

    def test_payload_signature_is_valid(self):
        # calculated via https://www.devglan.com/online-tools/hmac-sha256-online
        expected_wc_signature = "HfbFpdP8Je5naosPVWiBwEdAcLtNrxsPuDzOJMPafGM="

        request = RequestFactory().post(
            "/path/", self.original_payload, content_type="application/json"
        )
        request.META["HTTP_X_WC_WEBHOOK_SIGNATURE"] = expected_wc_signature

        result = SignatureValidation().authenticate(request)
        self.assertEqual(result, (self.user, None))
