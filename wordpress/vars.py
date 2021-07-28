import sys
import os
import logging

TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'

logger = logging.getLogger('django.tests')

if TESTING:
    wp_host = "https://wcfmmp_testing_host"
    wp_user = "test_wcfmmp_user"
    wp_password = "test_wcfmmp_password"
    wp_partner_role = "test_partner_role"
else:
    wp_host = os.getenv('WCFMMP_HOST')
    wp_user = os.getenv('WCFMMP_USER')
    wp_password = os.getenv('WCFMMP_PASSWORD')
    wp_partner_role = os.getenv('WP_PARTNER_ROLE')
