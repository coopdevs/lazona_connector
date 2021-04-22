import re


class Vendor():
    def __init__(self, id, name):
        self.id = id
        self.name = name

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

    def to_dict(self):
        return self.line_item

    # Finds the vendor attributes from all the metadata entries
    def _find_vendor(self):
        for datum in self.metadata:
            if datum['key'] == '_vendor_id':
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
