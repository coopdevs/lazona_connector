import re
import requests
import logging


class APIClient():
    API_PATH = "wp-json/wcfmmp/v1"
    PATH = "settings"

    def __init__(self, logger):
        self.client = requests
        api_base = "http://staging.lazona.coop"
        self.api_url = f'{api_base}/{self.API_PATH}'
        self.logger = logger

    def request(self, url):
        abs_url = f'{self.api_url}/{self.PATH}/{url}'
        self.logger.info(f'Wcfmpp request. url={abs_url}')

        return self.client.get(abs_url)


class Vendor():
    def __init__(
        self,
        id,
        name,
        address=None,
        zip=None,
        city=None,
        state=None,
        country=None,
        email=None,
        phone=None,
        client=requests,
        logger=logging.getLogger('django.server')
    ):
        self.client = APIClient(logger)

        self.id = id
        self.name = name
        self.address = address
        self.zip = zip
        self.city = city
        self.state = state
        self.country = country
        self.email = email
        self.phone = phone

    def get(self):
        response = self.client.request(f"id/{self.id}")
        self._convert_to_resource(response)
        return self

    def _convert_to_resource(self, response):
        body = response.json()

        self.address = body['address']['street_1']
        self.zip = body['address']['zip']
        self.city = body['address']['city']
        self.state = body['address']['state']
        self.country = body['address']['country']
        self.email = body['store_email']
        self.phone = body['phone']

    def __eq__(self, other):
        if not isinstance(other, Vendor):
            return NotImplemented

        return self.id == other.id and self.name == other.name


class LineItem():
    def __init__(self, line_item):
        self.quantity = line_item['quantity']
        self.metadata = line_item['meta_data']
        vendor = self._find_vendor()
        self.vendor = Vendor(vendor[0], vendor[1])

    # Finds the vendor attributes from all the metadata entries
    def _find_vendor(self):
        for datum in self.metadata:
            if datum['key'] == '_vendor_id':
                return datum['value'], datum['display_value']

        raise Exception("No _vendor_id provided in line item's metadata")


class Shipping():
    def __init__(self, shipping):
        self.first_name = shipping['first_name']
        self.last_name = shipping['last_name']
        self.address_1 = shipping['address_1']
        self.address_2 = shipping['address_2']
        self.postcode = shipping['postcode']
        self.city = shipping['city']
        self.state = shipping['state']
        self.country = shipping['country']


class Billing():
    def __init__(self, billing):
        self.phone = self._phone(billing['phone'])
        self.email = billing['email']

    def _phone(self, phone):
        if re.match(r'^\+\d{2}', phone):
            return phone[3:]
        else:
            return phone
