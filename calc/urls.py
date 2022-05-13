from django.contrib import admin
from django.urls import path, include

from . import views
from .views import ThermalView, ApiMaterialElements

urlpatterns = [
    path('api/v1/get/material-elements', ApiMaterialElements.as_view(), name='api_material_elements'),
    path('thermal', ThermalView.as_view(), name='thermal'),
    path('barrel', views.barrel, name='barrel'),
    path('forming', views.forming, name='forming'),
]
