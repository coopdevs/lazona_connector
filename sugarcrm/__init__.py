import os
import logging

rest_url = os.getenv("SUGARCRM_REST_URL")
username = os.getenv("SUGARCRM_USER")
password = os.getenv("SUGARCRM_PASSWORD")
membership_roles = os.getenv("SUGARCRM_MEMBERSHIP_ROLES")
if membership_roles:
    membership_roles = membership_roles.split(",")
logger = logging.getLogger("django.server")
