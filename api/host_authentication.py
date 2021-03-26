from django.contrib.auth.models import User
from rest_framework import authentication
from rest_framework import exceptions


class HostAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):
        source = request.META.get('X-WC-Webhook-Source')
        if not source:
            return None

        if 'staging.lazona.coop' not in source:
            raise exceptions.AuthenticationFailed('Invalid source host')

        try:
            user = User.objects.get(username='pau')
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such user')

        return (user, None)
