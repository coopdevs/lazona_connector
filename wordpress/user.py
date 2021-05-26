import wordpress
from wordpress.client import APIClient


class WPUser:
    def __init__(self, client=APIClient(), logger=wordpress.logger):
        self.logger = logger
        self.roles = set()
        self.client = client
        self.email = None
        self.roles = None
        self.user_id = None

    def fetch(self, email):
        response = self.client.get_request(f'users/?search={email}')
        body = response.json()
        if len(body):
            user_id = body[0]['id']
            response = self.client.post_request(f'users/{user_id}')
            body = response.json()
            email_profile = body['email']
            if email == email_profile:
                self._convert_to_resource(response)

        return self

    def _convert_to_resource(self, response):
        body = response.json()
        self.roles = body['roles']
        self.username = body['username']
        self.email = body['email']
        self.user_id = body['id']

    def update_as_partner(self):
        if wordpress.wp_partner_role not in self.roles:
            new_roles = ",".join(self.roles + wordpress.wp_partner_role)
            response = self.client.post_request(f'users/{self.user_id}', data={'roles': new_roles})
            response.raise_for_status()
            self.roles.append(wordpress.wp_partner_role)
