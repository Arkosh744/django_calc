# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from .forms.forming import FormingForm
from .forms.thermal import ThermalForm, ThermalZonesForm


def thermal(request):
    html_form = ThermalForm()
    html_form_zones = ThermalZonesForm()
    return render(request, 'calc/thermal.html', context={'html_form': html_form, 'html_form_zones': html_form_zones})


def barrel(request):
    return render(request, 'calc/barrel.html')


def forming(request):
    html_form = FormingForm()
    return render(request, 'calc/forming.html', context={'html_form': html_form})
