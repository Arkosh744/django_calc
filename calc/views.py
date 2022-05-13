# Create your views here.
import json

import plotly
import plotly.graph_objs as go
from django.forms import formset_factory
from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.views import View

from .forms.forming import FormingForm
from .forms.thermal import ThermalForm, ThermalZones, ThermalZonesFormSet
from .models import ThermalProps, PreparedData, ChemistryThermal
from .processing.thermal import main as calc_results


class ThermalView(View):
    html_forms = ThermalForm()
    geometry_forms = {1: 'Пластина', 2: 'Цилиндр', 3: 'Шар'}

    def get(self, request):
        ZonesFormset = formset_factory(ThermalZones, extra=1, formset=ThermalZonesFormSet)
        formset = ZonesFormset()
        return render(request, 'calc/thermal.html',
                      context={'html_forms': self.html_forms, 'zones_formset': formset,
                               'geometry_forms': 1,})

    def post(self, request):
        self.html_forms = ThermalForm(request.POST or None)
        ZonesFormset = formset_factory(ThermalZones, extra=int(request.POST.get('number_of_zones')),
                                       formset=ThermalZonesFormSet)
        formset = ZonesFormset(request.POST or None, prefix='form')
        print(formset.is_valid())
        print(formset.cleaned_data)
        # print(request.POST)

        prepared_data = PreparedData(thickness=float(request.POST.get('thickness')),
                                     point_layers=int(request.POST.get('thickness_layers')),
                                     temp_ini=float(request.POST.get('temp_initial')),
                                     form=int(request.POST.get('geometry')) - 1,
                                     time_in_zones=[float(i) for i in request.POST.getlist('form-0-zone_time')],
                                     time_step=float(request.POST.get('time_step')),
                                     k2=[float(i) for i in request.POST.getlist('form-0-zone_thermal_coef')],
                                     temp_e2=[float(i) for i in request.POST.getlist('form-0-zone_temp_air')])
        prepared_data.k1 = [float(i) for i in request.POST.getlist('form-0-zone_thermal_coef_bottom')] if \
            request.POST.get('geometry')[0] == '1' else [0]
        prepared_data.temp_e1 = [float(i) for i in request.POST.getlist('form-0-zone_temp_bottom')] if \
            request.POST.get('geometry')[0] == '1' else [0]

        cooling_form = True if prepared_data.temp_ini >= prepared_data.temp_e2[0] else False
        get_mat_name = ChemistryThermal.objects.filter(id=request.POST.get('material_select'))[0].name
        try:
            material = ThermalProps.objects.filter(name=get_mat_name, cooling=cooling_form)[0]
        except IndexError:
            material = ThermalProps.objects.filter(get_mat_name)[0]

        prepared_data.material_data = material

        calculated_results = calc_results(prepared_data)

        thickness_text = 'Толщина, мм' if int(request.POST.get('geometry')) - 1 == 0 else 'Радиус, мм'

        table_data = list()
        for table_row in range(int(request.POST.get('thickness_layers'))):
            table_data_row = list()
            table_data_row += [round(calculated_results.get('thickness_points')[table_row] * 1000, 2)]
            for temp_zone in range(int(request.POST.get('number_of_zones'))):
                table_data_row += [round(calculated_results.get('result_temp')[temp_zone][table_row], 1)]
            table_data += [table_data_row]

        thickness_points = [round(i * 1000, 2) for i in calculated_results.get('thickness_points')]

        graphJSON = self.plotly_create_thermal(calculated_results, request, thickness_points, thickness_text)

        initial_data_text = 'Марка стали: ' + material.name + '\n' + \
                       'Форма тела: ' + self.geometry_forms.get(int(request.POST.get('geometry'))) + '\n' + \
                       thickness_text + ': ' + str(prepared_data.thickness) + '\n' + \
                       'Начальная температура, °C:' + str(prepared_data.temp_ini) + '\n' + \
                       'Количество зон: ' + request.POST.get('number_of_zones') + '\n'


        return render(request, 'calc/thermal.html',
                      context={'html_forms': self.html_forms,
                               'number_of_zones': range(1, int(request.POST.get('number_of_zones')) + 1),
                               'zones_formset': formset,
                               'table_data': table_data, 'geometry_forms': int(request.POST.get('geometry')),
                               'plot': graphJSON,
                               'thickness_text': thickness_text,
                               'initial_data': initial_data_text})

    @staticmethod
    def plotly_create_thermal(calculated_results, request, thickness_points, thickness_text):
        fig = go.Figure()
        for i in range(int(request.POST.get('number_of_zones'))):
            fig.add_trace(go.Scatter(x=calculated_results.get('result_temp')[i], y=thickness_points,
                                     mode='lines+markers',
                                     name=f'Зона' + f'{i + 1}'))
        fig.update_xaxes(
            title_text="Температура, °C",
            title_font={"size": 14},
            title_standoff=8)
        fig.update_yaxes(
            title_text=thickness_text,
            title_font={"size": 14},
            title_standoff=8)
        fig.update_layout(template="simple_white")
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return graphJSON


class ApiMaterialElements(View):
    html_forms = ThermalForm()
    geometry_forms = {1: 'Пластина', 2: 'Цилиндр', 3: 'Шар'}

    def get(self, request):
        return HttpResponseNotFound()

    def post(self, request):
        self.html_forms = ThermalForm(request.POST or None)




def barrel(request):
    return render(request, 'calc/barrel.html')


def forming(request):
    html_form = FormingForm()
    return render(request, 'calc/forming.html', context={'html_form': html_form})
