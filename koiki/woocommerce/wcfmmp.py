import requests
import logging

import koiki


class APIClient():
    api_path = "wp-json/wcfmmp/v1"
    api_url = f'{koiki.wcfmmp_host}/{api_path}'

    def __init__(self, client=requests, logger=logging.getLogger('django.server')):
        self.client = client
        self.logger = logger

    def request(self, path):
        abs_url = f'{self.api_url}/{path}'
        self.logger.info(f'Wcfmpp request. url={abs_url}')

        return self.client.get(abs_url)
