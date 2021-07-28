import requests
import koiki.vars


class APIClient():
    api_path = "wp-json/wcfmmp/v1"
    api_url = f'{koiki.vars.wcfmmp_host}/{api_path}'

    def __init__(self, client=requests, logger=koiki.vars.logger):
        self.client = client
        self.logger = logger
        self.user = koiki.vars.wcfmmp_user
        self.password = koiki.vars.wcfmmp_password

    def request(self, path):
        abs_url = f'{self.api_url}/{path}'
        self.logger.info(f'Wcfmpp request. url={abs_url}')

        response = self.client.get(abs_url, auth=(self.user, self.password))
        response.raise_for_status()

        return response
