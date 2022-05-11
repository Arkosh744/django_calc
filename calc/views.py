# Create your views here.
from django.shortcuts import render
from django.views import View

from .forms.forming import FormingForm
from .forms.thermal import ThermalForm, ThermalZonesForm, MaterialSelectorForm, AdvancedThermalForm
from .models import ThermalProps, PreparedData, ChemistryThermal
from .processing.thermal import main as calc_results


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
                                     form=int(request.POST.get('geometry')) - 1,
                                     time_in_zones=[float(i) for i in request.POST.getlist('zone_time')],
                                     time_step=float(request.POST.get('time_step')),
                                     k2=[float(i) for i in request.POST.getlist('zone_thermal_coef')],
                                     temp_e2=[float(i) for i in request.POST.getlist('zone_temp_air')])
        prepared_data.k1 = [float(i) for i in request.POST.getlist('zone_thermal_coef_bottom')] if \
            request.POST.get('geometry')[0] == '1' else [0]
        prepared_data.temp_e1 = [float(i) for i in request.POST.getlist('zone_temp_bottom')] if \
            request.POST.get('geometry')[0] == '1' else [0]

        cooling_form = True if prepared_data.temp_ini >= prepared_data.temp_e2[0] else False
        get_mat_name = ChemistryThermal.objects.filter(id=request.POST.get('material_select'))[0].name
        try:
            material = ThermalProps.objects.filter(name=get_mat_name, cooling=cooling_form)[0]
        except IndexError:
            material = ThermalProps.objects.filter(get_mat_name)[0]

        prepared_data.material_data = material

        calculated_results = calc_results(prepared_data)
        print(calculated_results.get('result_temp'))
        table_data = list()
        for table_row in range(int(request.POST.get('thickness_layers'))):
            table_data_row = list()
            table_data_row += [calculated_results.get('thickness_points')[table_row] * 1000]
            for temp_zone in range(int(request.POST.get('number_of_zones'))):
                table_data_row += [round(calculated_results.get('result_temp')[temp_zone][table_row], 1)]
            table_data += [table_data_row]
            # table_data += [calculated_results.thickness_points[table_row]]
        print(table_data)


        return render(request, 'calc/thermal.html',
                      context={'html_forms': self.html_forms,
                               'number_of_zones': range(1, int(request.POST.get('number_of_zones'))+1),
                               'table_data': table_data,})


def barrel(request):
    return render(request, 'calc/barrel.html')


def forming(request):
    html_form = FormingForm()
    return render(request, 'calc/forming.html', context={'html_form': html_form})
