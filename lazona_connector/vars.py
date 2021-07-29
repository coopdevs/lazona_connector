import sys
import os
import logging

TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'

if TESTING:
    koiki_host = "https://testing_host"
    koiki_auth_token = "testing_auth_token"
    koiki_tracking_host = "https://testing_tracking_host"
    koiki_tracking_auth_token = "testing_autj_token"
    wcfmmp_host = "https://wcfmmp_testing_host"
    wcfmmp_user = "test_wcfmmp_user"
    wcfmmp_password = "test_wcfmmp_password"
    error_mail_recipients = ["test@test.com"]
    logger = logging.getLogger('django.server')
    wp_host = "https://wcfmmp_testing_host"
    wp_user = "test_wcfmmp_user"
    wp_password = "test_wcfmmp_password"
    wp_partner_role = "test_partner_role"
    redis_url = "rediss://test"
    sugarcrm_rest_url = 'https://test_sugarcrm_host'
    sugarcrm_username = 'test_sugarcrm_user'
    sugarcrm_password = 'test_sugarcrm_password'
    sugarcrm_membership_roles = ["^member^", "^is_partner^"]
else:
    koiki_host = os.getenv('KOIKI_HOST')
    koiki_auth_token = os.getenv('KOIKI_AUTH_TOKEN')
    koiki_tracking_host = os.getenv('KOIKI_TRACKING_HOST')
    koiki_tracking_auth_token = os.getenv('KOIKI_TRACKING_AUTH_TOKEN')
    wcfmmp_host = os.getenv('WCFMMP_HOST')
    wcfmmp_user = os.getenv('WCFMMP_USER')
    wcfmmp_password = os.getenv('WCFMMP_PASSWORD')
    error_mail_recipients = os.getenv("KOIKI_ERROR_MAIL_RECIPIENTS", "").split(",")
    logger = logging.getLogger('django.server')
    wp_host = os.getenv('WCFMMP_HOST')
    wp_user = os.getenv('WCFMMP_USER')
    wp_password = os.getenv('WCFMMP_PASSWORD')
    wp_partner_role = os.getenv('WP_PARTNER_ROLE')
    redis_url = os.getenv('REDIS_URL')
    sugarcrm_rest_url = os.getenv("SUGARCRM_REST_URL")
    sugarcrm_username = os.getenv("SUGARCRM_USER")
    sugarcrm_password = os.getenv("SUGARCRM_PASSWORD")
    sugarcrm_membership_roles = os.getenv("SUGARCRM_MEMBERSHIP_ROLES")
    if sugarcrm_membership_roles:
        sugarcrm_membership_roles = sugarcrm_membership_roles.split(",")
