from rest_framework import status
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse, path
from django.http import HttpResponse, HttpResponseRedirect

from .models import Shipment, ShipmentStatus
from koiki.woocommerce.woocommerce import APIClient
from api.serializers import OrderSerializer
from api.tasks import create_or_update_delivery, update_delivery_status
from .forms import ShipmentModelForm


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ("pk", "updated_at", "status", "delivery_id", "order_id", "vendor_id")
    list_filter = ("status",)
    search_fields = ("delivery_id",)
    readonly_fields = (
        "shipment_actions",
        "updated_at",
        "tracking_status_created_at",
        "tracking_updated_at"
    )
    form = ShipmentModelForm

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:shipment_id>/delivery/retry/",
                self.admin_site.admin_view(self.retry_delivery),
                name="retry-delivery",
            ),
            path(
                "<int:shipment_id>/delivery/update-status/",
                self.admin_site.admin_view(self.update_delivery_status),
                name="update-delivery-status",
            ),
        ]

        return custom_urls + urls

    def retry_delivery(self, request, shipment_id):
        client = APIClient()
        shipment = Shipment.objects.get(id=shipment_id)
        response = client.request(f"orders/{shipment.order_id}")
        serializer = OrderSerializer(data=response.json())
        if serializer.is_valid():
            order = serializer.validated_data
            create_or_update_delivery(order, vendor_id=str(shipment.vendor_id))
            return HttpResponseRedirect(reverse("admin:api_shipment_change", args=(shipment.id,)))

        return HttpResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update_delivery_status(self, request, shipment_id):
        shipment = Shipment.objects.get(pk=shipment_id)
        if not shipment.delivery_id:
            return HttpResponse(
                _("No es pot executar l'acció. No tenim Id de l'enviament"),
                status=status.HTTP_400_BAD_REQUEST
            )
        success = update_delivery_status(shipment.delivery_id)
        if success:
            return HttpResponseRedirect(reverse("admin:api_shipment_change", args=(shipment.id,)))
        return HttpResponse(
            _("La crida a la API no s'ha realitzat correctament"),
            status=status.HTTP_400_BAD_REQUEST
        )

    def _get_alert_msg(self, shipment):
        if shipment.status != ShipmentStatus.ERROR_FROM_BODY:
            return "if(confirm('Segur/a? Un enviament al transportista ja ha sigut realitzat.'))"
        else:
            return ""

    def shipment_actions(self, obj):
        if obj.id:
            return format_html(
                '<a class="button" href="javascript:{} window.location.href = \'{}\'">{}</a>'
                .format(
                    self._get_alert_msg(obj),
                    reverse("admin:retry-delivery", args=[obj.id]),
                    _("Reintentar enviament"),
                )
                + ' <a class="button" href="{}">{}</a>'.format(
                    reverse("admin:update-delivery-status", args=[obj.id]),
                    _("Actualitzar estat de l'enviament"),
                )
            )

    shipment_actions.short_description = _("Accions")
