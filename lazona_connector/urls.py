from django.conf.urls import url
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    path('api/', include('api.urls')),
]
