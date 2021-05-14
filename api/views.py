from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from api.authentication import SignatureValidation
from api.serializers import OrderSerializer
from api.tasks import create_delivery


class DeliveryList(APIView):
    authentication_classes = [SignatureValidation]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.validated_data
            create_delivery.delay(order)

            return Response(status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
