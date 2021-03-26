from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth.models import User

from api.host_authentication import HostAuthentication
import rest_framework


class HostAuthenticationTests(TestCase):

    def test_empty_header(self):
        request = RequestFactory().post('')
        result = HostAuthentication().authenticate(request)
        self.assertEqual(result, None)

    def test_invalid_host(self):
        request = RequestFactory().post('')
        request.META['X-WC-Webhook-Source'] = 'dummy.lazona.coop'

        self.assertRaises(
                rest_framework.exceptions.AuthenticationFailed,
                HostAuthentication().authenticate,
                request)

    def test_user_does_not_exist(self):
        request = RequestFactory().post('')
        request.META['X-WC-Webhook-Source'] = 'staging.lazona.coop'

        self.assertRaises(
                rest_framework.exceptions.AuthenticationFailed,
                HostAuthentication().authenticate,
                request)

    def test_user_exists(self):
        user = User(username='pau')
        user.save()

        request = RequestFactory().post('')
        request.META['X-WC-Webhook-Source'] = 'staging.lazona.coop'

        result = HostAuthentication().authenticate(request)
        self.assertEqual(result, (user, None))
