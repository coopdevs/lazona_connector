from rest_framework import serializers


class ShippingSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    address_1 = serializers.CharField(max_length=100)
    address_2 = serializers.CharField(max_length=100, allow_blank=True)
    postcode = serializers.CharField(min_length=5, max_length=5)
    city = serializers.CharField(max_length=100)
    state = serializers.CharField(max_length=100)
    country = serializers.CharField(max_length=100)


class BillingSerializer(serializers.Serializer):
    phone = serializers.CharField(min_length=9, max_length=12)
    email = serializers.EmailField()


class DeliverySerializer(serializers.Serializer):
    order_key = serializers.CharField(required=True)
    customer_note = serializers.CharField(max_length=100, allow_blank=True)
    shipping = ShippingSerializer()
    billing = BillingSerializer()
