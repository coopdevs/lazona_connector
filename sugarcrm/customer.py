import sugarcrm
from sugarcrm.client import APIClient


class Customer:
    def __init__(self, api_client=APIClient(), logger=sugarcrm.logger):
        self.logger = logger
        self.roles = set()
        self.api_client = api_client

    def fetch(self, email):
        # In SugarCRM personal individuals are in Accounts module and organizations in Contacts
        account_id, contact_id = self.api_client.search_email(email)
        roles_as_account = roles_as_contact = ""
        if account_id:
            roles_as_account = self.api_client.get_field(
                "Accounts", account_id, "stic_relationship_type_c"
            )
        if contact_id:
            roles_as_contact = self.api_client.get_field(
                "Contacts", contact_id, "stic_relationship_type_c"
            )
        self.roles = set(roles_as_account.split(",") + roles_as_contact.split(","))
        if "" in self.roles:
            self.roles.remove("")

        return self

    def check_is_partner(self):
        for role in self.roles:
            if role in sugarcrm.membership_roles:
                self.logger.info("Customer has partner role in the CRM")
                return True
        self.logger.info("Customer does not have partner role in the CRM")
        return False
