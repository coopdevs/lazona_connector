from django.contrib import admin

from .models import PersistentDelivery


@admin.register(PersistentDelivery)
class PersistentDeliveryAdmin(admin.ModelAdmin):

    list_display = ("shippment", "status", "order", "vendor")
    list_filter = ("status",)
    search_fields = ("shippment",)
    readonly_fields = ("shippment", "order", "vendor")
