import json
import base64
import hmac
import hashlib
import os

from django.contrib.auth.models import User
from rest_framework import authentication
from rest_framework import exceptions


def generate_woocommerce_signature(body, secret):
    digest = hmac.new(secret.encode('utf-8'), body, hashlib.sha256).digest()
    return base64.b64encode(digest).decode()


class HostAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):
        source = request.META.get('HTTP_X_WC_WEBHOOK_SOURCE')
        if not source:
            return None

        if 'staging.lazona.coop' not in source:
            raise exceptions.AuthenticationFailed('Invalid source host')

        try:
            user = User.objects.get(username='pau')
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such user')

        return (user, None)


class SignatureValidation(authentication.BaseAuthentication):
    def authenticate(self, request):
        signature = request.META.get("HTTP_X_WC_WEBHOOK_SIGNATURE")
        generated_signature = generate_woocommerce_signature(
            request.body, os.getenv("WC_WEBHOOK_SECRET")
        )

        if signature != generated_signature:
            raise exceptions.ValidationError("Invalid payload checksum signature")

        try:
            user = User.objects.get(username="pau")
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed("No such user")

        return (user, None)
