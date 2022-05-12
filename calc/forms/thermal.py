from django import forms

from calc.models import ChemistryThermal

geometry_state = (
    ("1", "Пластина"),
    ("2", "Цилиндр"),
    ("3", "Шар"),
)

zones_state = (
    (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8),
    # (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15)
)


class MaterialSelectorForm(forms.Form):
    material_select = forms.ModelChoiceField(label='Марка стали', queryset=ChemistryThermal.objects.all(),
                                             empty_label='Выберите материал', initial=3,
                                             widget=forms.Select(attrs={'class': 'form-control-small form-select'}))


class ThermalForm(forms.Form):
    geometry = forms.ChoiceField(choices=geometry_state, label='Форма',
                                 widget=forms.RadioSelect(), initial=1, )

    thickness = forms.FloatField(label='Толщина, мм', min_value=0, initial=30,
                                 widget=forms.TextInput(attrs={'class': "form-control form-control-small"}))
    temp_initial = forms.IntegerField(label='Начальная температура, °C', min_value=-73,
                                      initial=30,
                                      widget=forms.TextInput(attrs={'class': "form-control form-control-small"}))
    number_of_zones = forms.ChoiceField(label='Количество зон', choices=zones_state, initial=0,
                                        widget=forms.Select(attrs={'class': 'form-select form-control-small'}))


class ThermalZonesForm(forms.Form):
    zone_time = forms.FloatField(label='Время в зоне, сек', min_value=0,
                                 initial=10, widget=forms.TextInput(attrs={'class': "form-control form-control-small"}))
    zone_temp_air = forms.FloatField(label='Температура окр. среды, °C', min_value=0,
                                     initial=150,
                                     widget=forms.TextInput(attrs={'class': "form-control form-control-small"}))
    zone_temp_bottom = forms.FloatField(label='Температура поверхности, сек', min_value=-73,
                                        initial=150,
                                        widget=forms.TextInput(attrs={'class': "form-control form-control-small"}))

    zone_thermal_coef = forms.FloatField(label='Коэф. теплопередачи, Вт/м²К', min_value=0,
                                         initial=1500,
                                         widget=forms.TextInput(attrs={'class': "form-control form-control-small"}))
    zone_thermal_coef_bottom = forms.FloatField(label='Коэф. теплопередачи с поверхностью, Вт/м²К', min_value=0,
                                                initial=1500,
                                                widget=forms.TextInput(attrs={'class': "form-control form-control-small"}))


class AdvancedThermalForm(forms.Form):
    thickness_layers = forms.FloatField(label='Количество слоев по толщине', min_value=0, max_value=100, initial=5,
                                        widget=forms.TextInput(attrs={'class': "form-control form-control-small"}))
    time_step = forms.IntegerField(label='Шаг по времени, сек', min_value=0, max_value=5,
                                   initial=0.1,
                                   widget=forms.TextInput(attrs={'class': "form-control form-control-small"}))

