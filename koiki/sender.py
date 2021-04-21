class Sender():

    """Encapsulates the sender information to be provided to all Koiki deliveries"""

    # Note telefonoRemi can only have 9 digits.
    def __init__(self, line_item):
        self.line_item = line_item

    def to_dict(self):
        metadata = self.line_item['meta_data'][0]
        return {
            'nombreRemi': metadata['display_value'],
            'apellidoRemi': metadata['value'],
            'numeroCalleRemi': '',
            'direccionRemi': 'C/ La Zona, 1',
            'codPostalRemi': '08186',
            'poblacionRemi': 'Barcelona',
            'provinciaRemi': 'Barcelona',
            'paisRemi': 'ES',
            'emailRemi': 'lazona@opcions.org',
            'telefonoRemi': '518888191',
        }
