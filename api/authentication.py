import base64
import hmac
import hashlib
import os

from django.contrib.auth.models import User
from rest_framework import authentication
from rest_framework import exceptions


class HostAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):
        source = request.META.get('HTTP_X_WC_WEBHOOK_SOURCE')
        if not source:
            return None

        if 'staging.lazona.coop' not in source:
            raise exceptions.AuthenticationFailed('Invalid source host')

        user = User.objects.filter(is_superuser=True).first()
        if not user:
            raise exceptions.AuthenticationFailed('No such user')

        return (user, None)


class SignatureValidation(authentication.BaseAuthentication):
    def generate_woocommerce_signature(self, body, secret):
        digest = hmac.new(secret.encode('utf-8'), body, hashlib.sha256).digest()
        return base64.b64encode(digest).decode()

    def authenticate(self, request):
        signature = request.META.get("HTTP_X_WC_WEBHOOK_SIGNATURE")
        if not signature:
            return None

        generated_signature = self.generate_woocommerce_signature(
            request.body, os.getenv("WC_WEBHOOK_SECRET")
        )

        if signature != generated_signature:
            raise exceptions.AuthenticationFailed("Invalid payload checksum signature")

        user = User.objects.filter(is_superuser=True).first()
        if not user:
            raise exceptions.AuthenticationFailed('No such user')

        return (user, None)
