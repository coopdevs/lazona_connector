import requests

import koiki


class APIClient():
    api_path = "wp-json/wcfmmp/v1"
    api_url = f'{koiki.wcfmmp_host}/{api_path}'

    def __init__(self, client=requests, logger=koiki.logger):
        self.client = client
        self.logger = logger
        self.user = koiki.wcfmmp_user
        self.password = koiki.wcfmmp_password

    def request(self, path):
        abs_url = f'{self.api_url}/{path}'
        self.logger.info(f'Wcfmpp request. url={abs_url}')

        response = self.client.get(abs_url, auth=(self.user, self.password))
        response.raise_for_status()

        return response
