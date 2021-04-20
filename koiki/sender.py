class Sender():

    """Encapsulates the sender information to be provided to all Koiki deliveries"""

    # Note telefonoRemi can only have 9 digits.
    def to_dict(self):
        return {
            'nombreRemi': 'La Zona',
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
