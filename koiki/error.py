class Error():

    def __init__(self, body):
        self.body = body

    def to_dict(self):
        return {'error': self._error()}

    def _error(self):
        if 'mensaje' in self.body:
            return self.body['mensaje']
        elif 'error' in self.body:
            return self.body.get('error')
        else:
            return 'unknown'
