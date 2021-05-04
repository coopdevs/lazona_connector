import requests

import koiki


class APIClient():
    api_path = "wp-json/wcfmmp/v1"
    api_url = f'{koiki.wcfmmp_host}/{api_path}'

    def __init__(self, client=requests, logger=koiki.logger):
        self.client = client
        self.logger = logger

    def request(self, path):
        abs_url = f'{self.api_url}/{path}'
        self.logger.info(f'Wcfmpp request. url={abs_url}')

        response = self.client.get(abs_url, auth=(koiki.wcfmmp_user, koiki.wcfmmp_password))
        response.raise_for_status()

        return response
