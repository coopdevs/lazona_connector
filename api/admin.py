from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse, path
from django.http import HttpResponse
from .models import Shipment
from koiki.client import Client


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):

    list_display = ("pk", "delivery_id", "status", "order_id", "vendor_id")
    list_filter = ("status",)
    search_fields = ("delivery_id",)
    readonly_fields = ("shipment_actions",)

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
        return HttpResponse(f"retrying delivery of {shipment_id}")

    def update_delivery_status(self, request, shipment_id):
        shipment_model = Shipment.objects.get(pk=shipment_id)
        response = Client().update_delivery_status(shipment_model.delivery_id)
        return HttpResponse(f"updating delivery status of {shipment_id}")


    def shipment_actions(self, obj):
        if obj.pk:
            return format_html(
                '<a class="button" href="{}">{}</a>'.format(
                    reverse("admin:retry-delivery",
                    args=[obj.pk]),
                    _("Reintentar enviament")
                ) +
                '<a class="button" href="{}">{}</a>'.format(
                    reverse("admin:update-delivery-status",
                    args=[obj.pk]),
                    _("Actualitzar estat de l'enviament")
                )
            )

    shipment_actions.short_description = _("Accions")
