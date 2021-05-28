import httpretty
import logging
from django.conf import settings

import wordpress

httpretty.enable(allow_net_connect=False)

wordpress.wp_host = 'https://test_wp_host'
wordpress.wp_user = 'test_wp_user'
wordpress.wp_password = 'test_wp_password'
wordpress.wp_partner_role = "test_partner_role"

wordpress.logger = logging.getLogger('django.tests')

settings.CELERY_ALWAYS_EAGER = True
