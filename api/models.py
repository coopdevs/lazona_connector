from django.db import models
from django.utils.translation import ugettext_lazy as _


class DeliveryStatus(models.TextChoices):
    ERROR = "ERROR", _(u"Error del Transportista")
    SUCCESS = "SUCCESS", _(u"Signatura enviada al venedor")


class PersistentDelivery(models.Model):
    shipment = models.CharField(max_length=100, null=False, blank=False)
    order = models.IntegerField(null=False, blank=False)
    vendor = models.IntegerField(null=False, blank=False)
    pdf = models.CharField(max_length=200, null=True, blank=True)
    req_body = models.TextField(null=False, blank=False)
    req_response = models.TextField(null=True, blank=True)
    status = models.CharField(
        _(u"Estat de l'enviament"),
        max_length=20,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.SUCCESS,
        null=False,
        blank=False,
    )
