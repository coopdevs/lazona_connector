import os

from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth.models import User
from django.conf import settings

from api.authentication import SignatureValidation
import rest_framework


class SignatureValidationTests(TestCase):
    def setUp(self):
        os.environ["WC_WEBHOOK_SECRET"] = "testcase"
        self.original_payload = '{"test": 1 }'
        # calculated via https://www.devglan.com/online-tools/hmac-sha256-online
        self.expected_wc_signature = "UyKdg7msIA67rxmmf7JcLMUkzMKGLvfptk2NaSuyRQM="

    def test_payload_signature_is_invalid(self):
        invalid_wc_signature = "AAAA"

        request = RequestFactory().post(
            "/path/", self.original_payload, content_type="application/json"
        )
        request.META["HTTP_X_WC_WEBHOOK_SIGNATURE"] = invalid_wc_signature
        self.assertRaises(
            rest_framework.exceptions.AuthenticationFailed,
            SignatureValidation().authenticate,
            request,
        )

    def test_payload_signature_is_valid(self):
        user = User(username=settings.WC_WEBHOOK_USER)
        user.save()

        request = RequestFactory().post(
            "/path/", self.original_payload, content_type="application/json"
        )
        request.META["HTTP_X_WC_WEBHOOK_SIGNATURE"] = self.expected_wc_signature

        result = SignatureValidation().authenticate(request)
        self.assertEqual(result, (user, None))

    def test_payload_signature_valid_without_user(self):

        request = RequestFactory().post(
            "/path/", self.original_payload, content_type="application/json"
        )
        request.META["HTTP_X_WC_WEBHOOK_SIGNATURE"] = self.expected_wc_signature

        self.assertRaises(
            rest_framework.exceptions.AuthenticationFailed,
            SignatureValidation().authenticate,
            request,
        )
