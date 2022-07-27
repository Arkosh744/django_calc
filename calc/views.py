# Create your views here.
import copy
import csv
import json
import datetime
import io
import math

import xlsxwriter

import plotly
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from django.forms import formset_factory
from django.http import HttpResponseNotFound, HttpResponse, FileResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views import View
from xlsxwriter.utility import xl_col_to_name

from .forms.forming import FormingForm
from .forms.thermal import ThermalForm, ThermalZones, ThermalZonesFormSet
from .forms.wear_resistance import WearResistForm
from .models import ThermalProps, PreparedData, ChemistryThermal, CalculatedResults, TubeForming, WearProps
from .processing import tube_expander_forming
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

        result_dict_data_2, graphJSON, graphJSON_2, number_of_zones, table_data, thickness_text, result_object = \
            self.valid_data_processing(formset, request)

        table_data = self.squish_table(table_data)
        table_2_data = self.table_2_prepare_data(result_dict_data_2)

        return render(request, 'calc/thermal.html',
                      context={'html_forms': self.html_forms,
                               'number_of_zones': range(1, number_of_zones + 1),  # Для генерации таблицы результатов
                               'zones_formset': formset,
                               'table_2_data': table_2_data,
                               'table_data': table_data, 'geometry_forms': int(request.POST.get('geometry')),
                               'plot': graphJSON,
                               'plot_2': graphJSON_2,
                               'thickness_text': thickness_text,
                               'result_object': result_object,
                               })

    def table_2_prepare_data(self, result_dict):
        table_2 = {'table2_time': list(), 'table2_temp': list(), 'table2_speed': list()}
        table_2_data = list()
        for i in range(len(result_dict['time_x1'])):
            table_2['table2_time'] += result_dict['time_x1'][i]
            table_2['table2_temp'] += result_dict['cooling_speed_y1'][i]
            table_2['table2_speed'] += result_dict['temp_time_y2'][i]
        if len(table_2['table2_time']) > 9:
            table_2['table2_time'] = self.squish_table(table_2['table2_time'])
        if len(table_2['table2_temp']) > 9:
            table_2['table2_temp'] = self.squish_table(table_2['table2_temp'])
        if len(table_2['table2_speed']) > 9:
            table_2['table2_speed'] = self.squish_table(table_2['table2_speed'])
        for i in range(len(table_2['table2_time'])):
            table_2_data += [[table_2['table2_time'][i], table_2['table2_speed'][i], table_2['table2_temp'][i]]]
        return table_2_data

    def squish_table(self, table_data):
        step = (len(table_data) / 9)
        current_step = 0
        new_table_data = list()
        while current_step < len(table_data):
            new_table_data += [table_data[math.floor(current_step)]]
            current_step += step
        new_table_data += [table_data[-1]] if new_table_data[-1] != table_data[-1] else []
        table_data = new_table_data[:]
        return table_data

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
        result_dict_data_2 = copy.deepcopy(result_dict)

        for item in result_dict.keys():
            result_dict[f'{item}'] = self.equalizer(result_dict.get(f'{item}'))
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

        return result_dict_data_2, graphJSON, graphJSON_2, number_of_zones, table_data, thickness_text, result_object

    def equalizer(self, list_1):
        largest_length = 0  # To define the largest length
        for length in list_1:
            if len(length) > largest_length:
                largest_length = len(length)  # Will define the largest length in data.

        for i, length in enumerate(list_1):
            if len(length) < largest_length:
                remainder = largest_length - len(length)  # Difference of length of particular list and largest length
                list_1[i].extend([None for i in range(remainder)])  # Add None through the largest length limit
        return list_1

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
            title_standoff=8,
            tickformat=".1f")
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


class ApiThermalMaterialElements(View):

    def get(self, request, material_chem_id):
        get_mat_by_id = get_object_or_404(ChemistryThermal, id=material_chem_id).__dict__

        if '_state' in get_mat_by_id: del get_mat_by_id['_state']
        if 'id' in get_mat_by_id: del get_mat_by_id['id']
        if 'name' in get_mat_by_id: del get_mat_by_id['name']

        return JsonResponse(get_mat_by_id, safe=False)


class ApiThermalExportExcel(View):
    """Дока библиотеки https://xlsxwriter.readthedocs.io/index.html """
    geometry_forms = {0: 'Пластина', 1: 'Цилиндр', 2: 'Шар'}

    def get(self, request, result_id):
        result_data = get_object_or_404(CalculatedResults, id=result_id)
        filename = f'Thermal, {result_data.steel_grade_name}, {result_data.created_at.strftime("%d.%m.%Y")}'
        buffer = self.create_xls_thermal(result_data)

        return FileResponse(buffer, as_attachment=True, filename=f'{filename}.xlsx')

    def create_xls_thermal(self, result_data):
        buffer = io.BytesIO()
        workbook = xlsxwriter.Workbook(buffer)
        worksheet_1 = workbook.add_worksheet('Исходные данные')
        worksheet_2 = workbook.add_worksheet('Рез-Температура')
        worksheet_3 = workbook.add_worksheet('Рез-Скорость_Изм_Темп')
        cell_format = workbook.add_format()
        cell_format.set_text_wrap()
        cell_format.set_align('center')
        cell_format.set_align('vcenter')
        chart_2 = workbook.add_chart({'type': 'scatter', 'subtype': 'smooth'})
        worksheet_2.insert_chart('J2', chart_2)
        chart_3 = workbook.add_chart({'type': 'scatter', 'subtype': 'smooth'})
        worksheet_3.insert_chart('C7', chart_3)
        worksheet_1.set_column(0, 0, 29)
        created_date_msk_time = (result_data.created_at + datetime.timedelta(hours=3)).strftime("%d.%m.%Y %H:%m")
        worksheet_1.write(0, 0, f'Расчет от {created_date_msk_time}')
        worksheet_1.write(2, 0, f'Марка стали')
        worksheet_1.write(2, 1, f'{result_data.steel_grade_name}')
        worksheet_1.write(3, 0, f'Геометрическая форма')
        worksheet_1.write(3, 1, f'{self.geometry_forms.get(int(result_data.geometry))}')
        worksheet_1.write(4, 0, f'Толщина, мм') if int(result_data.geometry) == 0 \
            else worksheet_1.write(4, 0, f'Радиус, мм')
        worksheet_1.write(4, 1, result_data.thickness)
        worksheet_1.write(5, 0, f'Начальная температура, °C')
        worksheet_1.write(5, 1, result_data.initial_temperature)
        worksheet_1.write(6, 0, f'Количество зон')
        worksheet_1.write(6, 1, result_data.zones_number)
        worksheet_1.write(8, 0, f'Настройки расчета:')
        worksheet_1.write(9, 0, f'Количество слоев по толщине:')
        worksheet_1.write(9, 1, result_data.thickness_layers)
        worksheet_1.write(10, 0, f'Шаг по времени, сек:')
        worksheet_1.write(10, 1, result_data.time_step)
        worksheet_1.write(12, 0, f'Зона:')
        worksheet_1.write(13, 0, f'Время нахождения по зонам, сек')
        worksheet_1.write(14, 0, f'Температура окр. среды сверху, °C') if int(result_data.geometry) == 0 \
            else worksheet_1.write(14, 0, f'Температура окр. среды, °C')
        worksheet_1.write(15, 0, f'Коэф. теплопередачи сверху, Вт/м²К') if int(result_data.geometry) == 0 \
            else worksheet_1.write(15, 0, f'Коэф. теплопередачи, Вт/м²К')
        worksheet_1.write(16, 0, f'Температура окр. среды снизу, по зонам, °C') if int(
            result_data.geometry) == 0 else None
        worksheet_1.write(17, 0, f'Коэф. теплопередачи снизу, Вт/м²К') if int(
            result_data.geometry) == 0 else None
        worksheet_1.write(20, 0, f'Результаты расчетов представлены на страницах 2 и 3')

        worksheet_2.write(0, 0, f'Распределение температур по толщине')
        worksheet_2.write(1, 0, f'Толщина, мм') if int(result_data.geometry) == 0 \
            else worksheet_2.write(1, 0, f'Радиус, мм')
        worksheet_3.write(0, 0, f'Изменение температур во времени')
        for i in range(result_data.zones_number):
            worksheet_1.write(12, i + 1, i + 1)
            worksheet_1.write(13, i + 1, result_data.time_in_zones[i])
            worksheet_1.write(14, i + 1, result_data.temp_in_zones[i])
            worksheet_1.write(15, i + 1, result_data.coef_in_zones[i])
            worksheet_1.write(16, i + 1, result_data.temp_in_zones_bottom[i]) if int(
                result_data.geometry) == 0 else None
            worksheet_1.write(17, i + 1, result_data.coef_in_zones_bottom[i]) if int(
                result_data.geometry) == 0 else None

            worksheet_2.write(1, i + 1, f'Зона {i + 1}')
            for j in range(result_data.thickness_layers):
                worksheet_2.write(j + 2, i, result_data.thickness_points[j]) if i == 0 else None
                worksheet_2.write(j + 2, i + 1, result_data.result_zones[i][j])

            for j in range(len(result_data.result_time[i]) + 1):
                if j == 0:
                    worksheet_3.write(j + 1, 4 * i, f'Зона {i + 1}',
                                      cell_format) if result_data.zones_number > 1 else None
                    worksheet_3.write(j + 2, 4 * i, f'Время, сек', cell_format)
                    worksheet_3.write(j + 2, 4 * i + 1, f'Температура, °C', cell_format)
                    worksheet_3.write(j + 2, 4 * i + 2, f'Скорость изм. темп-ры, °C/сек', cell_format)
                    worksheet_3.set_column(j + 2, 4 * i, 11)
                    worksheet_3.set_column(j + 2, 4 * i + 1, 15.5)
                    worksheet_3.set_column(j + 2, 4 * i + 2, 16)
                else:
                    worksheet_3.write(j + 2, 4 * i, result_data.result_time[i][j - 1])
                    worksheet_3.write(j + 2, 4 * i + 1, result_data.result_temperature[i][j - 1])
                    worksheet_3.write(j + 2, 4 * i + 2, result_data.result_change_rate[i][j - 1])

            chart_3.add_series({
                'name': f'Изменение температуры в зоне {i + 1}, °C',
                'values': f"'Рез-Скорость_Изм_Темп'!${xl_col_to_name(4 * i + 1, False)}$4:"
                          f"${xl_col_to_name(4 * i + 1, False)}${len(result_data.result_time[i]) + 3}",
                'categories': f"'Рез-Скорость_Изм_Темп'!${xl_col_to_name(4 * i, False)}$4:"
                              f"${xl_col_to_name(4 * i, False)}${len(result_data.result_time[i]) + 3}",
                'y2_axis': 1, })

            # Тут есть if == 0 чтобы не было скачка 0 в первой зоне
            if i != 0:
                chart_3.add_series({
                    'name': f'Скорость изм. темп-ры зоны {i + 1}, °C/сек',
                    'values': f"'Рез-Скорость_Изм_Темп'!${xl_col_to_name(4 * i + 2, False)}$4:"
                              f"${xl_col_to_name(4 * i + 2, False)}${len(result_data.result_time[i]) + 3}",
                    'categories': f"'Рез-Скорость_Изм_Темп'!${xl_col_to_name(4 * i, False)}$4:"
                                  f"${xl_col_to_name(4 * i, False)}$"
                                  f"{len(result_data.result_time[i]) + 3}"})
            else:
                chart_3.add_series({
                    'name': f'Скорость изм. темп-ры зоны {i + 1}, °C/сек',
                    'values': f"'Рез-Скорость_Изм_Темп'!${xl_col_to_name(4 * i + 2, False)}$5:"
                              f"${xl_col_to_name(4 * i + 2, False)}${len(result_data.result_time[i]) + 3}",
                    'categories': f"'Рез-Скорость_Изм_Темп'!${xl_col_to_name(4 * i, False)}$5:"
                                  f"${xl_col_to_name(4 * i, False)}${len(result_data.result_time[i]) + 3}"})

            chart_2.add_series({
                'name': f'Зона {i + 1}, °C',
                'categories': f"'Рез-Температура'!${xl_col_to_name(i + 1, False)}$3:"
                              f"${xl_col_to_name(i + 1, False)}${result_data.thickness_layers + 2}",
                'values': f"'Рез-Температура'!$A$3:$A${result_data.thickness_layers + 2}"})
        chart_2.set_title({'name': 'Распределение температур'})
        chart_2.set_x_axis({'name': 'Температура, °C', })
        chart_2.set_y_axis({'name': 'Толщина, мм'}) if int(result_data.geometry) == 0 else \
            chart_2.set_y_axis({'name': 'Радиус, мм'})
        chart_2.set_size({'width': 560, 'height': 360})

        chart_3.set_title({'name': 'Изменение температур во времени'})
        chart_3.set_x_axis({'name': 'Время, сек', })
        chart_3.set_y_axis({'name': 'Скорость изм. темп-ры, °C/сек'})
        chart_3.set_y2_axis({'name': 'Средняя температура, °C'})
        chart_3.set_size({'width': 880, 'height': 480})
        workbook.close()
        buffer.seek(0)
        return buffer


def barrel(request):
    return render(request, 'calc/barrel.html')


class FormingView(View):
    html_forms = FormingForm()

    def get(self, request):

        return render(request, 'calc/forming.html',
                      context={'html_forms': self.html_forms, })

    def post(self, request):
        self.html_forms = FormingForm(request.POST)
        material = TubeForming.objects.get(id=float(self.html_forms.data.get('material_select')))
        tube_radius = float(self.html_forms.data.get('tube_radius'))
        tube_thickness = float(self.html_forms.data.get('tube_thickness'))

        if tube_radius <= 2 * tube_thickness:
            error_variable = 'Ошибка: Радиус должен быть в 2 раза больше, чем толщина.'
            return render(request, 'calc/forming.html',
                          context={'html_forms': self.html_forms,
                                   'error_variable': error_variable, })

        tubes_values = tube_expander_forming.calc_new_tube_yield(props=material.tension_data,
                                                                 thickness=tube_thickness,
                                                                 radius=tube_radius)
        if tubes_values['PE_avg'] <= 0.3:
            error_variable = 'Пластические деформации в ходе расчета не обнаружены.'
            return render(request, 'calc/forming.html',
                          context={'html_forms': self.html_forms,
                                   'error_variable': error_variable, })

        return render(request, 'calc/forming.html',
                      context={'html_forms': self.html_forms, 'tubes_values': tubes_values, })


class WearView(View):
    html_forms = WearResistForm()

    def get(self, request):
        return render(request, 'calc/wear.html',
                      context={'html_forms': self.html_forms, })

    def post(self, request):
        self.html_forms = WearResistForm(request.POST)

        if not self.html_forms.is_valid():
            error_variable = 'Ошибка: Введите корректные данные.'
            return render(request, 'calc/wear.html',
                          context={'html_forms': self.html_forms, 'error_variable': error_variable})

        material = WearProps.objects.get(id=float(self.html_forms.data.get('steel_grades_select')))
        material_2 = WearProps.objects.get(id=float(self.html_forms.data.get('steel_grades_select_2')))
        lifespan = 6000
        thickness = float(self.html_forms.data.get('thickness'))
        thickness_2 = float(self.html_forms.data.get('thickness_2'))
        if thickness <= 0 or thickness_2 <= 0:
            error_variable = 'Ошибка: Толщина должна быть больше 0.'
            return render(request, 'calc/wear.html',
                          context={'html_forms': self.html_forms, 'error_variable': error_variable})

        abrasiveness = float(self.html_forms.data.get('abrasiveness'))
        abrasiveness_2 = float(self.html_forms.data.get('abrasiveness_2'))
        if abrasiveness <= 0 or abrasiveness_2 <= 0:
            error_variable = 'Ошибка: Абразивность должна быть больше 0.'
            return render(request, 'calc/wear.html',
                          context={'html_forms': self.html_forms, 'error_variable': error_variable})

        price = float(self.html_forms.data.get('price'))
        price_2 = float(self.html_forms.data.get('price_2'))

        lifespan_2 = (lifespan * material_2.wear_value * thickness_2 * abrasiveness) / (
                    material.wear_value * thickness * abrasiveness_2)
        lifespan_new = round(((lifespan_2 - lifespan) / lifespan)*100, 1)
        weight_new = round(((thickness_2 - thickness) / thickness)*100, 1)

        lifespan_color = "green" if lifespan_new >= 0 else "red"
        weight_color = "green" if weight_new <= 0 else "red"

        wear_results = {'lifespan_new': abs(lifespan_new),
                        'weight_new': abs(weight_new),
                        'lifespan_color': lifespan_color,
                        'weight_color': weight_color}
        if price > 0 and price_2 > 0:
            total_price = (price * thickness) / lifespan
            total_price_2 = (price_2 * thickness_2) / lifespan_2
            print(thickness, thickness_2, lifespan, lifespan_2)
            print(total_price, total_price_2)
            price_new = round(((total_price_2 - total_price) / total_price)*100, 1)
            price_color = "green" if price_new <= 0 else "red"
            wear_results['price_color'] = price_color
            wear_results['price_new'] = abs(price_new)

        return render(request, 'calc/wear.html',
                      context={'html_forms': self.html_forms, 'wear_results': wear_results, })
