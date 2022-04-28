# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from .forms.forming import FormingForm
from .forms.thermal import ThermalForm, ThermalZonesForm, MaterialSelectorForm, AdvancedThermalForm


def thermal(request):

    html_forms = {'material_selector_form': MaterialSelectorForm(),
                  'base_form': ThermalForm(),
                  'base_zones_form': ThermalZonesForm(),
                  'advanced_form': AdvancedThermalForm()}

    return render(request, 'calc/thermal.html', context={'html_forms': html_forms})


def barrel(request):
    return render(request, 'calc/barrel.html')


def forming(request):
    html_form = FormingForm()
    return render(request, 'calc/forming.html', context={'html_form': html_form})
