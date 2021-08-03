from django.db import models
from django.utils.translation import ugettext_lazy as _


class ShipmentStatus(models.TextChoices):
    ERROR_FROM_BODY = "ERROR_FROM_BODY", _(u"Error alta enviament")
    LABEL_SENT = "LABEL_SENT", _(u"Etiqueta enviada al venedor")
    IN_PROCESS = "IN_PROCESS", _(u"En proces")
    ON_HOLD = "ON_HOLD", _(u"Particularitat al proces d'enviament")
    ERROR_FROM_TRACKING = "ERROR_FROM_TRACKING", _(u"Error API de seguiment")
    DELIVERED = "DELIVERED", _(u"Entregat"),


class Shipment(models.Model):
    delivery_id = models.CharField(
        _("Id de l'enviament"),
        max_length=100, null=False, blank=True
    )
    order_id = models.IntegerField(
        _("Id de la comanda de WooCommerce"),
        null=False, blank=False
    )
    vendor_id = models.IntegerField(
        _("Id del vendor de WooCommerce"),
        null=False, blank=False
    )
    label_url = models.CharField(
        _("Url de l'etiqueta"),
        max_length=200, blank=True
    )
    status = models.CharField(
        _("Estat de l'enviament"),
        max_length=20,
        choices=ShipmentStatus.choices,
        null=False,
        blank=False,
    )
    updated_at = models.DateTimeField(
        _("Última actualització creació"),
        auto_now=True
    )
    tracking_updated_at = models.DateTimeField(
        _("Última actualització seguiment"),
        auto_now=True
    )
    tracking_status_created_at = models.DateTimeField(
        _("Data de creació del darrer estat de l'enviament"),
        null=True, auto_now=False, blank=True
    )
    req_body = models.CharField(
        _("Cos de la petició de la comanda enviat"),
        max_length=300, blank=True
    )
    delivery_message = models.CharField(
        _("Missatge de seguiment"),
        max_length=300, blank=True
    )
    delivery_notes = models.CharField(
        _("Notes de seguiment"),
        max_length=300, blank=True
    )

    def __str__(self):
        return '{}: (wc_order:{}, vendor:{})'.format(self.pk, self.order_id, self.vendor_id)
