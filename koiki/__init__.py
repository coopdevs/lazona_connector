import os
import logging

host = os.getenv('KOIKI_HOST')
wcfmmp_host = os.getenv('WCFMMP_API_BASE')
logger = logging.getLogger('django.server')
