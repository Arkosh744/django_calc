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
        ZonesFormset = formset_factory(ThermalZones, extra=8, formset=ThermalZonesFormSet)
        formset = ZonesFormset()
        return render(request, 'calc/thermal.html',
                      context={'html_forms': self.html_forms, 'zones_formset': formset, 'geometry_forms': 1,})

    def post(self, request):
        ZonesFormset = formset_factory(ThermalZones, formset=ThermalZonesFormSet)
        formset = ZonesFormset(request.POST or None, prefix='form')
        self.html_forms = ThermalForm(request.POST or None)

        if not self.html_forms.is_valid() or not formset.is_valid():
            return render(request, 'calc/thermal.html',
                          context={'html_forms': self.html_forms, 'zones_formset': formset})

        number_of_zones = int(self.html_forms.cleaned_data.get('number_of_zones'))
        prepared_data = PreparedData(thickness=self.html_forms.cleaned_data.get('thickness'),
                                     point_layers=self.html_forms.cleaned_data.get('thickness_layers'),
                                     temp_ini=self.html_forms.cleaned_data.get('temp_initial'),
                                     form=int(self.html_forms.cleaned_data.get('geometry')) - 1,
                                     time_step=self.html_forms.cleaned_data.get('time_step'),
                                     )

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
        get_mat_name = ChemistryThermal.objects.get(id=request.POST.get('material_select')).name
        try:
            material = ThermalProps.objects.get(name=get_mat_name, cooling=cooling_form)
        except ThermalProps.DoesNotExist:
            material = ThermalProps.objects.get(name=get_mat_name)

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
                               'number_of_zones': range(1, number_of_zones + 1), # Для генерации таблицы результатов
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
