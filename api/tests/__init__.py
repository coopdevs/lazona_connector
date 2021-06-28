import httpretty
import logging
import os
from django.conf import settings

import koiki
import wordpress

httpretty.enable(allow_net_connect=False)

koiki.host = 'https://testing_host'

koiki.wcfmmp_host = 'https://wcfmmp_testing_host'
koiki.wcfmmp_user = 'test_wcfmmp_user'
koiki.wcfmmp_password = 'test_wcfmmp_password'
koiki.error_mail_recipients = ['admin@email.com']
koiki.logger = logging.getLogger('django.tests')
koiki.auth_token = 'testing_auth_token'

wordpress.wp_host = 'https://wp_testing_host'
wordpress.wp_user = 'test_wp_user'
wordpress.wp_password = 'test_wp_password'

settings.CELERY_ALWAYS_EAGER = True
settings.WC_WEBHOOK_USER = 'test_user'

os.environ['REDIS_URL'] = 'rediss://test'
