import sugarcrm
from sugarcrm.api import SugarCrmAPI


class Client:
    def __init__(self, logger=sugarcrm.logger):
        self.logger = logger

    def check_customer_is_partner(self, customer):
        crm_api = SugarCrmAPI(sugarcrm.rest_url, sugarcrm.username, sugarcrm.password)

        # In SugarCRM personal individuals are in Accounts module and organizations in Contacts
        customer_email = customer["email"]
        account_id, contact_id = crm_api.search_email(customer_email)
        roles_as_account = roles_as_contact = ""
        if account_id:
            roles_as_account = crm_api.get_field(
                "Accounts", account_id, "stic_relationship_type_c"
            )
        if contact_id:
            roles_as_contact = crm_api.get_field(
                "Contacts", contact_id, "stic_relationship_type_c"
            )
        crm_roles = set(roles_as_account.split(",") + roles_as_contact.split(","))
        if '' in crm_roles:
            crm_roles.remove('')
        self.logger.info("Found roles in CRM: {}".format(crm_roles))
        for role in crm_roles:
            # if the user in the crm has a role that it is considered as a LaZona partner/membership
            if role in sugarcrm.membership_roles:
                self.logger.info("{} has the partner role in the CRM".format(customer_email))
                return True
        self.logger.info("{} does not have the partner role in the CRM".format(customer_email))
        return False
