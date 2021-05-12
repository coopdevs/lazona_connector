from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from api.authentication import HostAuthentication, SignatureValidation
from api.serializers import OrderSerializer, CustomerSerializer
from api.tasks import create_delivery, check_customer_is_partner


class DeliveryList(APIView):
    authentication_classes = [TokenAuthentication, HostAuthentication, SignatureValidation]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.validated_data
            create_delivery.delay(order)

            return Response(status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerList(APIView):
    authentication_classes = [TokenAuthentication, HostAuthentication, SignatureValidation]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.validated_data
            check_customer_is_partner.delay(customer)

            return Response(status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
