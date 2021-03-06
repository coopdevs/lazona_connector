import httpretty
import logging

import koiki

httpretty.enable(allow_net_connect=False)

koiki.host = 'https://testing_host'

koiki.wcfmmp_host = 'https://wcfmmp_testing_host'
koiki.wcfmmp_user = 'test_wcfmmp_user'
koiki.wcfmmp_password = 'test_wcfmmp_password'

koiki.logger = logging.getLogger('django.tests')
koiki.auth_token = 'testing_auth_token'
