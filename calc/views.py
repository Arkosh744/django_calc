# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from .forms.forming import FormingForm
from .forms.thermal import ThermalForm, ThermalZonesForm, MaterialSelectorForm, AdvancedThermalForm
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.views import View
from .processing.thermal import main as calc_results
from .models import ThermalProps, PreparedData


class ThermalView(View):
    html_forms = {'material_selector_form': MaterialSelectorForm(),
                  'base_form': ThermalForm(),
                  'base_zones_form': ThermalZonesForm(),
                  'advanced_form': AdvancedThermalForm()}

    def get(self, request):
        return render(request, 'calc/thermal.html', context={'html_forms': self.html_forms})

    def post(self, request):
        print(request.POST)
        prepared_data = PreparedData(thickness=float(request.POST.get('thickness')[0]),
                                     point_layers=int(request.POST.get('thickness_layers')[0]),
                                     temp_ini=float(request.POST.get('temp_initial')[0]),
                                     form=int(request.POST.get('geometry')[0]),
                                     time_in_zones=request.POST.get('zone_time'),
                                     time_step=request.POST.get('time_step'),
                                     k2=request.POST.get('zone_thermal_coef'),
                                     temp_e2=request.POST.get('zone_temp_air'))
        if int(request.POST.get('geometry')[0]) == 1:
            prepared_data.k1 = request.POST.get('zone_thermal_coef_bottom')
            prepared_data.temp_e1 = request.POST.get('zone_thermal_coef_bottom')

        cooling_form = True
        try:
            material = ThermalProps.objects.filter(id=request.POST.get('material_select'), cooling=cooling_form)[0]
        except IndexError:
            print('IndexError')
            material = ThermalProps.objects.filter(id=request.POST.get('material_select'))[0]
        prepared_data.material_data = material

        print(prepared_data)
        initial_data = {'material': material.id,}
        # calc_results(material, request.POST)
        return render(request, 'calc/thermal.html', context={'html_forms': self.html_forms})


def barrel(request):
    return render(request, 'calc/barrel.html')


def forming(request):
    html_form = FormingForm()
    return render(request, 'calc/forming.html', context={'html_form': html_form})
