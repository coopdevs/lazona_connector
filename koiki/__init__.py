import os
import logging

host = os.getenv('KOIKI_HOST')
wcfmmp_host = os.getenv('WCFMMP_API_BASE')
logger = logging.getLogger('django.server')
auth_token = os.getenv('KOIKI_AUTH_TOKEN')
