import responses
from unittest import TestCase
from unittest.mock import MagicMock, patch
from wordpress.user import WPUser
from wordpress.client import APIClient
from api.tasks import update_user_as_partner


class WPUserTest(TestCase):
    def setUp(self):
        self.mock_client = MagicMock()
        self.api_client = APIClient()
        self.email = "email@email.com"
        self.user_id = 13
        self.partner_role = "test_partner_role"

    @responses.activate
    def test_fetch_wp_user(self):
        wp_user = WPUser(self.api_client)
        responses.add(
            responses.GET,
            f"https://wcfmmp_testing_host/wp-json/wp/v2/users/?search={self.email}",
            status=200,
            json=[{"id": self.user_id}],
        )

        responses.add(
            responses.GET,
            f"https://wcfmmp_testing_host/wp-json/wp/v2/users/{self.user_id}?context=edit",
            status=200,
            json={
                "id": self.user_id,
                "username": "testusername",
                "email": self.email,
                "roles": ["testrole"],
            },
        )

        wp_user.fetch_by_email(self.email)

        self.assertEqual(wp_user.roles, ["testrole"])
        self.assertEqual(wp_user.email, self.email)
        self.assertEqual(wp_user.username, "testusername")
        self.assertEqual(wp_user.user_id, self.user_id)

    @responses.activate
    def test_update_wp_user(self):
        wp_user = WPUser(self.api_client)
        wp_user.roles = ["previousrole"]

        responses.add(
            method=responses.POST,
            url=f"https://wcfmmp_testing_host/wp-json/wp/v2/users/{self.user_id}",
            status=200,
            json={
                "id": self.user_id,
                "roles": [self.partner_role],
                "username": "testusername",
                "email": self.email,
            },
        )
        wp_user.user_id = self.user_id
        wp_user.update(roles=self.partner_role)

        self.assertEqual(wp_user.roles, [self.partner_role])
        self.assertEqual(wp_user.email, self.email)
        self.assertEqual(wp_user.username, "testusername")
        self.assertEqual(wp_user.user_id, self.user_id)

    @patch("api.tasks.WPUser", autospec=True)
    def test_tasks_check_customer_is_not_partner(self, mock_wp_user):
        mock_wp_user.return_value = self.mock_client
        self.mock_client.fetch_by_email.return_value = self.mock_client
        self.mock_client.roles = ["customer"]

        update_user_as_partner(self.email)
        self.mock_client.fetch_by_email.assert_called_once_with(self.email)
        self.mock_client.update.assert_called_once_with(roles="test_partner_role")
