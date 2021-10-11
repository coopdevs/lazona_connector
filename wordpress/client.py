import requests
import lazona_connector.vars


class APIClient:
    api_path = "wp-json/wp/v2"

    def __init__(self, client=requests, logger=lazona_connector.vars.logger):
        self.client = client
        self.logger = logger
        self.user = lazona_connector.vars.wp_user
        self.password = lazona_connector.vars.wp_password
        self.api_url = f'{lazona_connector.vars.wp_host}/{self.api_path}'

    def get_request(self, path, params={}):
        abs_url = f'{self.api_url}/{path}'
        self.logger.info(f'WP GET request. url={abs_url}. params={params}')
        response = self.client.get(abs_url, params=params, auth=(self.user, self.password))
        response.raise_for_status()
        body = response.json()
        return body

    def post_request(self, path, data={}):
        abs_url = f'{self.api_url}/{path}'
        self.logger.info(f'WP POST request. url={abs_url}. data={data}')

        response = self.client.post(abs_url, auth=(self.user, self.password), data=data)
        response.raise_for_status()
        body = response.json()
        return body
