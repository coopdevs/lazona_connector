from django.db import models
from django.utils.translation import ugettext_lazy as _


class ShipmentStatus(models.TextChoices):
    ERROR_FROM_BODY = "ERROR_FROM_BODY", _(u"Error alta enviament")
    LABEL_SENT = "LABEL_SENT", _(u"Etiqueta enviada al venedor")


class Shipment(models.Model):
    delivery_id = models.CharField(max_length=100, null=False, blank=True, unique=False)
    order_id = models.IntegerField(null=False, blank=False)
    vendor_id = models.IntegerField(null=False, blank=False)
    label_url = models.CharField(max_length=200, blank=True)
    status = models.CharField(
        _(u"Estat de l'enviament"),
        max_length=20,
        choices=ShipmentStatus.choices,
        null=False,
        blank=False,
    )

    def __str__(self):
        return self.delivery_id
