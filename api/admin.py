from django.contrib import admin

from .models import Shipment


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):

    list_display = ("shipment", "status", "order", "vendor")
    list_filter = ("status",)
    search_fields = ("shipment",)
    readonly_fields = ("shipment", "order", "vendor")
