import sys
import os
import logging

TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'


if TESTING:
    host = "https://testing_host"
    wcfmmp_host = "https://wcfmmp_testing_host"
    wcfmmp_user = "test_wcfmmp_user"
    wcfmmp_password = "test_wcfmmp_password"
    auth_token = "testing_auth_token"
    error_mail_recipients = ["test@test.com"]
    logger = logging.getLogger('django.server')
    wp_host = "https://wcfmmp_testing_host"
    wp_user = "test_wcfmmp_user"
else:
    host = os.getenv('KOIKI_HOST')
    wcfmmp_host = os.getenv('WCFMMP_HOST')
    wcfmmp_user = os.getenv('WCFMMP_USER')
    wcfmmp_password = os.getenv('WCFMMP_PASSWORD')
    auth_token = os.getenv('KOIKI_AUTH_TOKEN')
    error_mail_recipients = os.getenv("KOIKI_ERROR_MAIL_RECIPIENTS", "").split(",")
    logger = logging.getLogger('django.server')
    wp_host = os.getenv('WCFMMP_HOST')
    wp_user = os.getenv('WCFMMP_USER')
