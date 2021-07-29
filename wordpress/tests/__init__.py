import httpretty
from django.conf import settings


httpretty.enable(allow_net_connect=False)
settings.CELERY_ALWAYS_EAGER = True
settings.WC_WEBHOOK_USER = 'test_user'
