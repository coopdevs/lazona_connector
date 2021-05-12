from django.urls import path
from api import views

app_name = 'deliveries'

urlpatterns = [
    path('deliveries/', views.DeliveryList.as_view(), name='create'),
    path('customers/check_is_partner/', views.CustomerList.as_view(), name='check_is_partner'),
]
