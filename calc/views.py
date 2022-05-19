# Create your views here.
import json
import datetime

import plotly
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from django.forms import formset_factory
from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.views import View

from .forms.forming import FormingForm
from .forms.thermal import ThermalForm, ThermalZones, ThermalZonesFormSet
from .models import ThermalProps, PreparedData, ChemistryThermal, CalculatedResults
from .processing.thermal import main as calc_results
from django.utils import timezone


class ThermalView(View):
    html_forms = ThermalForm()
    ZonesFormset = formset_factory(ThermalZones, extra=8, formset=ThermalZonesFormSet)
    geometry_forms = {1: 'Пластина', 2: 'Цилиндр', 3: 'Шар'}

    def get(self, request):
        formset = self.ZonesFormset()
        return render(request, 'calc/thermal.html',
                      context={'html_forms': self.html_forms, 'zones_formset': formset, 'geometry_forms': 1, })

    def post(self, request):
        formset = self.ZonesFormset(request.POST or None, prefix='form')
        self.html_forms = ThermalForm(request.POST or None)

        if not self.html_forms.is_valid() or not formset.is_valid():
            return render(request, 'calc/thermal.html',
                          context={'html_forms': self.html_forms, 'zones_formset': formset})

        calculated_results, graphJSON, graphJSON_2, number_of_zones, table_data, thickness_text, result_object = \
            self.valid_data_processing(formset, request)

        return render(request, 'calc/thermal.html',
                      context={'html_forms': self.html_forms,
                               'number_of_zones': range(1, number_of_zones + 1),  # Для генерации таблицы результатов
                               'zones_formset': formset,
                               'calculated_results': calculated_results['result_list'],
                               'table_data': table_data, 'geometry_forms': int(request.POST.get('geometry')),
                               'plot': graphJSON,
                               'plot_2': graphJSON_2,
                               'thickness_text': thickness_text,
                               'result_object': result_object,
                               })

    def valid_data_processing(self, formset, request):
        number_of_zones = int(self.html_forms.cleaned_data.get('number_of_zones'))
        prepared_data = PreparedData(thickness=self.html_forms.cleaned_data.get('thickness'),
                                     point_layers=self.html_forms.cleaned_data.get('thickness_layers'),
                                     temp_ini=self.html_forms.cleaned_data.get('temp_initial'),
                                     form=int(self.html_forms.cleaned_data.get('geometry')) - 1,
                                     time_step=self.html_forms.cleaned_data.get('time_step'))

        for zone in formset.cleaned_data[:number_of_zones]:
            prepared_data.time_in_zones.append(zone.get('zone_time'))
            prepared_data.k2.append(zone.get('zone_thermal_coef'))
            prepared_data.temp_e2.append(zone.get('zone_temp_air'))
            if prepared_data.form == 0:
                prepared_data.k1.append(zone.get('zone_thermal_coef_bottom'))
                prepared_data.temp_e1.append(zone.get('zone_temp_bottom'))
            else:
                prepared_data.k1 = [0]
                prepared_data.temp_e1 = [0]

        cooling_form = True if prepared_data.temp_ini >= prepared_data.temp_e2[0] else False
        get_mat_name = ChemistryThermal.objects.get(id=request.POST.get('material_select'))
        try:
            material = ThermalProps.objects.get(name=get_mat_name.name, cooling=cooling_form)
        except ThermalProps.DoesNotExist:
            material = ThermalProps.objects.get(name=get_mat_name.name)

        prepared_data.material_data = material
        calculated_results = calc_results(prepared_data)
        thickness_text = 'Толщина, мм' if int(request.POST.get('geometry')) - 1 == 0 else 'Радиус, мм'

        graphJSON, graphJSON_2, result_dict, table_data, thickness_points = self.make_graphs(calculated_results,
                                                                                             number_of_zones, request,
                                                                                             thickness_text)

        result_object = CalculatedResults.objects.create(created_at=timezone.now(),
                                                         expiration_date=timezone.now() + datetime.timedelta(days=1),
                                                         steel_grade_name=get_mat_name.name,
                                                         steel_grade_id_chemistry=get_mat_name,
                                                         steel_grade_id_prop=material,
                                                         geometry=prepared_data.form,
                                                         thickness=prepared_data.thickness,
                                                         thickness_points=thickness_points,
                                                         initial_temperature=prepared_data.temp_ini,
                                                         zones_number=number_of_zones,
                                                         time_in_zones=prepared_data.time_in_zones,
                                                         temp_in_zones=prepared_data.temp_e2,
                                                         coef_in_zones=prepared_data.k2,
                                                         temp_in_zones_bottom=prepared_data.temp_e1,
                                                         coef_in_zones_bottom=prepared_data.k1,
                                                         thickness_layers=prepared_data.point_layers,
                                                         time_step=prepared_data.time_step,
                                                         result_zones=calculated_results.get('result_temp'),
                                                         result_time=result_dict.get('time_x1'),
                                                         result_temperature=result_dict.get('temp_time_y2'),
                                                         result_change_rate=result_dict.get('cooling_speed_y1'), )

        return calculated_results, graphJSON, graphJSON_2, number_of_zones, table_data, thickness_text, result_object

    def make_graphs(self, calculated_results, number_of_zones, request, thickness_text):
        table_data = list()
        for table_row in range(int(request.POST.get('thickness_layers'))):
            table_data_row = list()
            table_data_row += [round(calculated_results.get('thickness_points')[table_row] * 1000, 2)]
            for temp_zone in range(int(request.POST.get('number_of_zones'))):
                table_data_row += [round(calculated_results.get('result_temp')[temp_zone][table_row], 1)]
            table_data += [table_data_row]
        thickness_points = [round(i * 1000, 2) for i in calculated_results.get('thickness_points')]

        graphJSON = self.plotly_create_thermal(calculated_results, request, thickness_points, thickness_text)
        graphJSON_2, result_dict = self.plotly_create_thermal_cooling(calculated_results, number_of_zones)

        return graphJSON, graphJSON_2, result_dict, table_data, thickness_points

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

    @staticmethod
    def plotly_create_thermal_cooling(calculated_results, number_of_zones):
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        cooling_speed_y1 = list()
        temp_time_y2 = list()
        time_x1 = list()
        for zone in calculated_results['result_list']:
            time_zone = list()
            temp_zone = list()
            speed_zone = list()
            for values in zone:
                time, temp, speed = values
                time_zone += [round(time, 2)]
                temp_zone += [round(temp, 1)]
                speed_zone += [round(speed, 2)]
            time_x1 += [time_zone]
            cooling_speed_y1 += [speed_zone]
            temp_time_y2 += [temp_zone]

        result_dict = {'time_x1': time_x1, 'cooling_speed_y1': cooling_speed_y1, 'temp_time_y2': temp_time_y2}

        for i in range(number_of_zones):
            if i == 0:
                fig.add_trace(go.Scatter(x=time_x1[i][1:],
                                         y=cooling_speed_y1[i][1:],
                                         mode='lines',
                                         name=f'Скорость изменения <br>температуры в зоне ' + f'{i + 1}, °C/c'),
                              secondary_y=True)
            else:
                fig.add_trace(go.Scatter(x=time_x1[i],
                                         y=cooling_speed_y1[i],
                                         mode='lines',
                                         name=f'Скорость изменения <br>температуры в зоне ' + f'{i + 1}, °C/c'),
                              secondary_y=True)

            fig.add_trace(go.Scatter(x=time_x1[i],
                                     y=temp_time_y2[i],
                                     mode='lines',
                                     name=f'Температура в зоне ' + f'{i + 1}, °C'), secondary_y=False)
            fig.add_vline(x=max(time_x1[i]), line_width=1, line_dash="dash")
        fig.update_xaxes(
            title_text="Время, сек",
            title_font={"size": 14},
            title_standoff=8)
        fig.update_yaxes(
            title_text='Скорость изменения температуры, °C/c',
            title_font={"size": 14},
            title_standoff=5, secondary_y=True)
        fig.update_yaxes(
            title_text='Температура, °C',
            title_font={"size": 14},
            title_standoff=8, secondary_y=False)
        fig.update_layout(template="simple_white")
        graphJSON_2 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return graphJSON_2, result_dict


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
