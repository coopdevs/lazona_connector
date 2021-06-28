import base64
import os

# TODO: convert this class into Django Model in order to link Koiki's shipping,
# with WC purchase and PDF
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from koiki import wcfmmp_host, logger, error_mail_recipients


class Delivery:
    pdf_folder = "pdf_barcodes"

    def __init__(self, data, vendor, req_body={}):
        self.data = data
        self.vendor = vendor
        self.req_body = req_body
        self.shipment_id = data["numPedido"]
        self.order_id = data["order_id"]

    def to_dict(self):
        return {
            "number": self.data["numPedido"],
            "barcode": self.data["codBarras"],
            "label": self.data["etiqueta"],
            "order_id": self.data["order_id"]
        }

    def _is_errored(self):
        return self.data.get("respuesta", "") != "101"

    def print_pdf(self):
        content = base64.b64decode(self.data["etiqueta"])

        pdf = open(os.path.join(self.pdf_folder, f"{self.shipment_id}.pdf"), "wb")
        pdf.write(content)
        pdf.close()

        return pdf

    def send_mail_to_vendor(self):
        self.print_pdf()
        context = {
            'url_wc_order': f'{wcfmmp_host}area-privada/orders-details/{self.order_id}'
        }
        logger.info('Sending Koiki pdf to email {}'.format(self.vendor.email))
        message = render_to_string('contact_template.txt', context)
        send_mail = EmailMessage(
            _("Enviament Koiki per a la comanda: {}").format(self.order_id),
            message,
            to=[self.vendor.email]
        )
        pdf = open(os.path.join(self.pdf_folder, f"{self.shipment_id}.pdf"), "rb")
        send_mail.attach(f"{self.shipment_id}.pdf", pdf.read(), "application/pdf")

        send_mail.send(fail_silently=False)

    def send_error_mail_to_admin(self):
        error_returned = self.data.get("mensaje")
        if not error_returned:
            error_returned = "Missatge d'error no proporcionat"
        context = {
            'url_wc_order': f'{wcfmmp_host}area-privada/orders-details/{self.order_id}',
            'req_body': self.req_body,
            'error_returned': error_returned,
        }
        logger.info('Sending Koiki error to admins for order {}'.format(self.order_id))
        message = render_to_string('error_template.txt', context)
        send_mail = EmailMessage(
            _("Error enviament Koiki per a la comanda: {}").format(self.order_id),
            message,
            to=error_mail_recipients
        )

        send_mail.send(fail_silently=False)
