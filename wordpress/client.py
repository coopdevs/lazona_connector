import requests
import wordpress

class APIClient:
    api_path = "wp-json/wp/v2"
    user = wordpress.wp_user
    password = wordpress.wp_password
    api_url = f'{wordpress.wp_host}/{api_path}'

    def __init__(self, client=requests, logger=wordpress.logger):
        self.client = client
        self.logger = logger

    def get_request(self, path):

        abs_url = f'{self.api_url}/{path}'

        self.logger.info(f'WP GET request. url={abs_url}')

        response = self.client.get(abs_url, auth=(self.user, self.password))
        response.raise_for_status()

        return response

    def post_request(self, path, data={}):
        abs_url = f'{self.api_url}/{path}'
        self.logger.info(f'WP POST request. url={abs_url}. data={data}')

        response = self.client.post(abs_url, auth=(self.user, self.password), data=data)
        response.raise_for_status()

        return response
