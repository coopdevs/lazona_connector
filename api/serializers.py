from rest_framework import serializers


class DeliverySerializer(serializers.Serializer):
    order_number = serializers.CharField(required=True, allow_blank=True, max_length=100)
