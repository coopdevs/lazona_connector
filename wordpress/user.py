import wordpress
from wordpress.client import APIClient


class WPUser:

    def __init__(self, client=APIClient(), logger=wordpress.logger):
        self.logger = logger
        self.roles = set()
        self.client = client
        self.email = None
        self.user_id = None
        self.roles = None
        self.username = None

    def fetch(self, email):
        body = self.client.get_request(f'users/?search={email}')
        if len(body):
            user_id = body[0]['id']
            self.fetch_by_email(user_id)
        return self

    def fetch_by_email(self, user_id):
        body = self.client.get_request(f'users/{user_id}?context=edit')
        self._convert_to_resource(body)
        return self

    def _convert_to_resource(self, body):
        self.roles = body['roles']
        self.username = body['username']
        self.email = body['email']
        self.user_id = body['id']

    def update(self, **kwargs):
        body = self.client.post_request(f'users/{self.user_id}', data=kwargs)
        self._convert_to_resource(body)
