import requests
import lazona_connector.vars


class APIClient():
    api_path = "wp-json/wc/v3"
    api_url = f'{lazona_connector.vars.wcfmmp_host}/{api_path}'

    def __init__(self, client=requests, logger=lazona_connector.vars.logger):
        self.client = client
        self.logger = logger
        self.user = lazona_connector.vars.wcfmmp_user
        self.password = lazona_connector.vars.wcfmmp_password

    def request(self, path):
        abs_url = f'{self.api_url}/{path}'
        self.logger.info(f'Woocommerce request. url={abs_url}')

        response = self.client.get(abs_url, auth=(self.user, self.password))
        response.raise_for_status()

        return response
