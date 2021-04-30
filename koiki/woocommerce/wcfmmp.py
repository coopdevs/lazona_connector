import requests
import logging


class APIClient():
    API_PATH = "wp-json/wcfmmp/v1"
    PATH = "settings"

    def __init__(self, client=requests, logger=logging.getLogger('django.server')):
        self.client = client
        api_base = "http://staging.lazona.coop"
        self.api_url = f'{api_base}/{self.API_PATH}'
        self.logger = logger

    def request(self, url):
        abs_url = f'{self.api_url}/{self.PATH}/{url}'
        self.logger.info(f'Wcfmpp request. url={abs_url}')

        return self.client.get(abs_url)
