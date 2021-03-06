from django.contrib import admin
from django.urls import path, include

from . import views
from .views import ThermalView, ApiThermalMaterialElements, ApiThermalExportExcel, FormingView, WearView

urlpatterns = [
    path('api/v1/get/material-elements/<material_chem_id>', ApiThermalMaterialElements.as_view(), name='api_material_elements'),
    path('api/v1/get/thermal-results/<result_id>', ApiThermalExportExcel.as_view(), name='api_thermal_export_excel'),
    path('thermal', ThermalView.as_view(), name='thermal'),
    path('barrel', views.barrel, name='barrel'),
    path('forming', FormingView.as_view(), name='forming'),
    path('wear-resistance', WearView.as_view(), name='wear-resistance'),
]
