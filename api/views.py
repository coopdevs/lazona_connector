from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from api.authentication import SignatureValidation
from api.serializers import OrderSerializer, CustomerSerializer
from api.tasks import create_or_update_delivery, update_customer_if_is_partner
from api.models import Shipment


class DeliveryList(APIView):
    authentication_classes = [SignatureValidation]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.validated_data
            already_created = Shipment.objects.filter(order_id=order['id']).exists()
            if not already_created:
                create_or_update_delivery.delay(order)
                return Response(status=status.HTTP_201_CREATED)
            else:
                return Response(status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerList(APIView):
    authentication_classes = [SignatureValidation]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.validated_data
            update_customer_if_is_partner.delay(customer['email'])

            return Response(status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
