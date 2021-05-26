import os
import logging

wp_host = os.getenv('WCFMMP_HOST')
wp_user = os.getenv('WCFMMP_USER')
wp_password = os.getenv('WCFMMP_PASSWORD')
wp_partner_role = os.getenv('WP_PARTNER_ROLE')

logger = logging.getLogger("django.server")
