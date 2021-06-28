import os
import logging

host = os.getenv('KOIKI_HOST')

wcfmmp_host = os.getenv('WCFMMP_HOST')
wcfmmp_user = os.getenv('WCFMMP_USER')
wcfmmp_password = os.getenv('WCFMMP_PASSWORD')

logger = logging.getLogger('django.server')
auth_token = os.getenv('KOIKI_AUTH_TOKEN')
error_mail_recipients = os.getenv("KOIKI_ERROR_MAIL_RECIPIENTS","").split(",")
