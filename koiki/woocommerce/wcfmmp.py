import requests
import logging

import koiki


class APIClient():
    API_PATH = "wp-json/wcfmmp/v1"

    def __init__(self, client=requests, logger=logging.getLogger('django.server')):
        self.client = client
        api_base = koiki.wcfmmp_api_base
        self.api_url = f'{api_base}/{self.API_PATH}'
        self.logger = logger

    def request(self, path):
        abs_url = f'{self.api_url}/{path}'
        self.logger.info(f'Wcfmpp request. url={abs_url}')

        return self.client.get(abs_url)
