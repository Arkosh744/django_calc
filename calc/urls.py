from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path('thermal', views.thermal, name='thermal'),
    path('barrel', views.barrel, name='barrel'),
    path('forming', views.forming, name='forming'),
]
