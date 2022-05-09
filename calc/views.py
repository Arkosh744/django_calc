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
        prepared_data = PreparedData(thickness=float(request.POST.get('thickness')),
                                     point_layers=int(request.POST.get('thickness_layers')),
                                     temp_ini=float(request.POST.get('temp_initial')),
                                     form=int(request.POST.get('geometry')),
                                     time_in_zones=[float(i) for i in request.POST.getlist('zone_time')],
                                     time_step=float(request.POST.get('time_step')),
                                     k2=[float(i) for i in request.POST.getlist('zone_thermal_coef')],
                                     temp_e2=[float(i) for i in request.POST.getlist('zone_temp_air')])
        prepared_data.k1 = [float(i) for i in request.POST.getlist('zone_thermal_coef_bottom')] if \
            request.POST.get('geometry')[0] == '1' else [0]
        prepared_data.temp_e1 = [float(i) for i in request.POST.getlist('zone_thermal_coef_bottom')] if \
            request.POST.get('geometry')[0] == '1' else [0]

        cooling_form = True if prepared_data.temp_ini >= prepared_data.temp_e2[0] else False

        try:
            material = ThermalProps.objects.filter(id=request.POST.get('material_select'), cooling=cooling_form)[0]
        except IndexError:
            material = ThermalProps.objects.filter(id=request.POST.get('material_select'))[0]

        prepared_data.material_data = material

        calculated_results = calc_results(prepared_data)
        # temp, res = iteration(tau, current_zone_time, temp, prepared_data.material_data,
        #                       prepared_data.form, h, r_pos, r_posn, r_posp,
        #                       prepared_data.k2[current_zone], prepared_data.temp_e2[current_zone],
        #                       prepared_data.k1[0], prepared_data.temp_e1[0], prepared_data.point_layers)

        return render(request, 'calc/thermal.html', context={'html_forms': self.html_forms})


def barrel(request):
    return render(request, 'calc/barrel.html')


def forming(request):
    html_form = FormingForm()
    return render(request, 'calc/forming.html', context={'html_form': html_form})
