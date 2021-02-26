from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from api.serializers import DeliverySerializer
from koiki.client import Client

class DeliveryList(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DeliverySerializer(data=request.data)
        if serializer.is_valid():
            order = {
                'order_key': 'xxx',
                'shipping': {
                    'first_name': 'John',
                    'last_name': 'Lennon',
                    'address_1': 'Beatles Street 66',
                    'address_2': '',
                    'postcode': '08032',
                    'city': 'Barcelona',
                    'state': 'Barcelona',
                    'country': 'Spain'
                },
                'billing': {
                    'phone': '666666666',
                    'email': 'lennon@example.com'
                }
            }
            Client(order).create_delivery()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
