from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from api import views

app_name = 'deliveries'

urlpatterns = [
    path('deliveries/', views.DeliveryList.as_view(), name='create'),
]
