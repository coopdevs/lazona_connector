import httpretty
import logging
from django.conf import settings

import sugarcrm

httpretty.enable(allow_net_connect=False)

sugarcrm.rest_url = 'https://test_sugarcrm_host'
sugarcrm.username = 'test_sugarcrm_user'
sugarcrm.password = 'test_sugarcrm_password'
sugarcrm.membership_roles = ["^member^", "^is_partner^"]

sugarcrm.logger = logging.getLogger('django.tests')

settings.CELERY_ALWAYS_EAGER = True
