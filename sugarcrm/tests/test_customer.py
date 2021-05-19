from unittest import TestCase
from unittest.mock import MagicMock
from sugarcrm.customer import Customer


class CustomerTest(TestCase):
    def setUp(self):
        self.mock_client = MagicMock()
        self.email = "email@email.com"
        self.roles_from_crm_as_partner = "^is_partner^,^is_role_test^"
        self.roles_from_crm_not_as_partner = "^is_not_partner^,^is_role_test^"

    def test_customer_is_partner(self):
        customer = Customer()
        customer.api_client = self.mock_client
        self.mock_client.search_email.return_value = ("ACCOUNT_ID", "CONTACT_ID")
        self.mock_client.get_field.return_value = self.roles_from_crm_as_partner
        customer.fetch(self.email)

        self.assertIn("^is_partner^", customer.roles)
        self.assertTrue(customer.check_is_partner())

    def test_customer_is_not_partner(self):
        customer = Customer()
        customer.api_client = self.mock_client
        self.mock_client.search_email.return_value = ("ACCOUNT_ID", "CONTACT_ID")
        self.mock_client.get_field.return_value = self.roles_from_crm_not_as_partner
        customer.fetch(self.email)
        self.assertNotIn("^is_partner^", customer.roles)
        self.assertFalse(customer.check_is_partner())
