from rest_framework.authentication import TokenAuthentication
from api.authentication import HostAuthentication, SignatureValidation
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from api.serializers import OrderSerializer
from koiki.client import Client


class DeliveryList(APIView):
    authentication_classes = [TokenAuthentication, HostAuthentication, SignatureValidation]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.validated_data

            Client(order).create_delivery()

            return Response(order, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
