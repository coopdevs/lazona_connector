class Vendor():
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __eq__(self, other):
        if not isinstance(other, Vendor):
            return NotImplemented

        return self.id == other.id and self.name == other.name
