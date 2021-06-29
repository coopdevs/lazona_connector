import os.path
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.translation import gettext as _

from koiki import wcfmmp_host, logger, error_mail_recipients


class SuccessDeliveryMail:
    def __init__(self, delivery):
        self.pdf_path = delivery.print_pdf()
        self.recipient = delivery.vendor.email
        self.order_id = delivery.order_id

        context = {"url_wc_order": f"{wcfmmp_host}area-privada/orders-details/{self.order_id}"}

        self.message = render_to_string("contact_template.txt", context)

    def send(self):
        logger.info("Sending Koiki pdf to email {}".format(self.recipient))
        send_mail = EmailMessage(
            _("Enviament Koiki per a la comanda: {}").format(self.order_id),
            self.message,
            to=[self.recipient],
        )

        pdf_filename = os.path.basename(self.pdf_path)
        print('self.pdf_path', self.pdf_path)
        send_mail.attach(pdf_filename, open(self.pdf_path, "rb").read(), "application/pdf")

        return send_mail.send(fail_silently=False)


class FailedDeliveryMail:
    def __init__(self, delivery):
        self.order_id = delivery.order_id
        error_returned = delivery.data.get("mensaje")
        if not error_returned:
            error_returned = "Missatge d'error no proporcionat"
        context = {
            "url_wc_order": f"{wcfmmp_host}area-privada/orders-details/{self.order_id}",
            "req_body": delivery.req_body,
            "error_returned": error_returned,
        }
        self.message = render_to_string("error_template.txt", context)

    def send(self):
        logger.info("Sending Koiki error to admins for order {}".format(self.order_id))

        send_mail = EmailMessage(
            _("Error enviament Koiki per a la comanda: {}").format(self.order_id),
            self.message,
            to=error_mail_recipients,
        )

        return send_mail.send(fail_silently=False)
