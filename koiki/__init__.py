import os
import logging

host = os.getenv('KOIKI_HOST')
wcfmmp_api_base = os.getenv('WCFMMP_API_BASE')
logger = logging.getLogger('django.server')
