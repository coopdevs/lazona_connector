from koiki.woocommerce.wcfmmp import APIClient
from koiki.woocommerce.state import State
from wordpress.user import WPUser
import re


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
        phone=None
    ):
        self.client = APIClient()

        self.id = id
        self.name = name
        self.address = address
        self.zip = zip
        self.city = city
        self.state = self._build_state(state)
        self.country = country
        self.email = email
        self.phone = phone

    def fetch(self):
        if self.email is None:
            response = self.client.request(f"settings/id/{self.id}")
            self._convert_to_resource(response)
            self._fetch_email()
        return self

    def _fetch_email(self):
        wp_user = WPUser().fetch_by_id(self.id)
        self.email = wp_user.email

    def _convert_to_resource(self, response):
        body = response.json()

        self.address = body['address']['street_1']
        self.zip = body['address']['zip']
        self.city = body['address']['city']
        self.state = self._build_state(body['address']['state'])
        self.country = self._build_country(body['address']['country'])
        self.phone = body['phone']

    def __eq__(self, other):
        if not isinstance(other, Vendor):
            return NotImplemented

        return self.id == other.id and self.name == other.name

    def _build_state(self, value):
        if value is None or value == '':
            return value
        else:
            return str(State(value))

    def _build_country(self, value):
        if value is None or value == '':
            return 'ES'
        else:
            return value


class LineItem():
    def __init__(self, line_item):
        self.quantity = line_item['quantity']
        self.metadata = line_item['meta_data']
        vendor = self._find_vendor()
        self.vendor = Vendor(id=vendor[0], name=vendor[1])

    # Finds the vendor attributes from all the metadata entries
    def _find_vendor(self):
        for datum in self.metadata:
            if datum['key'] == '_vendor_id':
                return datum['value'], datum['display_value']

        raise Exception("No _vendor_id provided in line item's metadata")


class ShippingLine():
    def __init__(self, line_item):
        self.method_title = line_item['method_title']
        self.method_id = line_item['method_id']
        self.metadata = line_item['meta_data']
        vendor = self._find_vendor()
        if vendor:
            self.vendor = Vendor(id=vendor[0], name=vendor[1])
        else:
            self.vendor = None

    # Finds the vendor attributes from all the metadata entries
    def _find_vendor(self):
        for datum in self.metadata:
            if datum['key'] == 'vendor_id':
                return datum['value'], datum['display_value']

        return None


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
