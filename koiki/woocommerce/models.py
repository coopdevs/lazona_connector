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
