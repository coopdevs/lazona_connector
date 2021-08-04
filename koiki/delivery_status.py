'''
# KOIKI DELIVERY STATES
100 ENVÍO PENDIENTE LLEGADA
102 LLEGADA A KOIKI
103 CLIENTE AVISADO
114 ENTREGA CONCERTADA
###############################
111 CLIENTE AUSENTE
112 RECHAZADO POR CLIENTE
113 DIRECCION INCORRECTA
900 CADUCADO
901 EN GESTION
902 FALTA
903 DESVIO
904 SOBRANTE
905 DEVOLUCION
906 NO TIENE DINERO
################################
108 ENTREGADO

# WC ORDER STATES
wc-pending
wc-processing
wc-on-hold
wc-completed
wc-cancelled
wc-refunded
wc-failed

# SHIPMENT STATES
ERROR_FROM_BODY = "ERROR_FROM_BODY", _(u"Error alta enviament")
LABEL_SENT = "LABEL_SENT", _(u"Etiqueta enviada al venedor")
IN_PROCESS = "IN_PROCESS", _(u"En proces")
ON_HOLD = "ON_HOLD", ._(u"Error proces enviament")
ERROR_FROM_TRACKING = "ERROR_FROM_TRACKING", _(u"Error API de seguiment")
DELIVERED = "DELIVERED", _(u"Entregat")
'''


class DeliveryStatus():

    def __init__(self, response_body={}):
        self.response_body = response_body

    in_process_koiki_codes = [100, 102, 103, 114]
    on_hold_koiki_codes = [111, 112, 113, 900, 901, 902, 903, 904, 905, 906]
    delivered_koiki_codes = [108]

    def to_dict(self):
        return {
            "response_message": self._get_current_val('codEstado'),
            "response_code": self._get_current_val('code'),
            "response_date": self._get_current_val('date', 'date'),
            "response_notes": self._get_current_val('notas'),
            "response_error_code": self._get_error_val('code'),
            "response_error_message": self._get_error_val('message'),
            "shipment_status": self._get_shipment_status(self._get_current_val('code'))
        }

    def is_errored(self):
        if self.response_body.get('error'):
            return True
        return False

    def get_data_val(self, key):
        return self.to_dict()[key]

    def _get_current_val(self, key, val_type='char'):
        try:
            val = self.response_body['result'][0][key]
        except(Exception):
            if val_type == 'char':
                val = ''
            if val_type == 'date':
                val = None
        return val

    def _get_error_val(self, key):
        try:
            val = self.response_body['error'][key]
        except(Exception):
            val = ''
        return val

    def _get_shipment_status(self, status_code):
        from api.models import ShipmentStatus
        if self.is_errored():
            return ShipmentStatus.ERROR_FROM_TRACKING
        else:
            if status_code in self.in_process_koiki_codes:
                return ShipmentStatus.IN_PROCESS
            if status_code in self.on_hold_koiki_codes:
                return ShipmentStatus.ON_HOLD
            if status_code in self.delivered_koiki_codes:
                return ShipmentStatus.DELIVERED
        return False

    # TODO: when sending status back to wc need to create this
    # def get_wc_order_status(self):
