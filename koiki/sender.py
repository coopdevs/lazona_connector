class Sender():

    # Note telefonoRemi can only have 9 digits.
    def __init__(self, vendor):
        self.vendor = vendor

    def to_dict(self):
        # TODO: find the actual _vendor_id key. Don't rely on the index
        return {
            'nombreRemi': self.vendor.name,
            'apellidoRemi': '',
            'numeroCalleRemi': '',
            'direccionRemi': 'C/ La Zona, 1',
            'codPostalRemi': '08186',
            'poblacionRemi': 'Barcelona',
            'provinciaRemi': 'Barcelona',
            'paisRemi': 'ES',
            'emailRemi': 'lazona@opcions.org',
            'telefonoRemi': '518888191',
        }
