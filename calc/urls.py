from django.contrib import admin
from django.urls import path, include

from . import views
from .views import ThermalView

urlpatterns = [
    path('thermal', ThermalView.as_view(), name='thermal'),
    path('barrel', views.barrel, name='barrel'),
    path('forming', views.forming, name='forming'),
]
