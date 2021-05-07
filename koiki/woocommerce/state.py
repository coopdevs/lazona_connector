import pycountry


class InvalidState(Exception):
    pass


class State():
    def __init__(self, code):
        full_code = f'ES-{code}'

        if code == 'Barcelona':
            full_code = 'ES-B'
        elif code == 'Girona':
            full_code = 'ES-GI'
        elif code == 'Tarragona':
            full_code = 'ES-T'
        elif code == 'Lleida':
            full_code = 'ES-L'

        self.value = pycountry.subdivisions.get(code=full_code)

        if self.value is None:
            raise InvalidState(code)

    def __str__(self):
        return self.value.name
