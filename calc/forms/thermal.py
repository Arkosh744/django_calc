from django import forms

from calc.models import ChemistryThermal

geometry_state = (
    ("1", "Пластина"),
    ("2", "Цилиндр"),
    ("3", "Шар"),
)


class ThermalForm(forms.Form):

    material_select = forms.ModelChoiceField(label='Марка стали', queryset=ChemistryThermal.objects.all(),
                                             empty_label='Выберите материал',
                                             widget=forms.Select(attrs={'class': 'form-select form-select-sm'}))

    geometry = forms.ChoiceField(choices=geometry_state, label='Форма',
                                 widget=forms.RadioSelect(), initial='1',)

    thickness = forms.FloatField(label='Толщина, мм', min_value=0, initial=30, widget=forms.TextInput(attrs={'class': "form-control form-control-sm"}))
    temp_initial = forms.IntegerField(label='Начальная температура, °C', min_value=-73,
                                      initial=30, widget=forms.TextInput(attrs={'class': "form-control form-control-sm"}))
    number_of_zones = forms.IntegerField(label='Количество зон', min_value=1, max_value=20,
                                         initial=1, widget=forms.TextInput(attrs={'class': "form-control form-control-sm"}))


class ThermalZonesForm(forms.Form):
    zone_time_1 = forms.FloatField(label='Время в зоне, сек', min_value=-73,
                                   initial=1, widget=forms.TextInput(attrs={'class': "form-control form-control-sm"}))
    thermal_coef_1 = forms.FloatField(label='Коэф. теплопередачи, ', min_value=0,
                                      initial=150, widget=forms.TextInput(attrs={'class': "form-control form-control-sm"}))
    temp_air_1 = forms.FloatField(label='Температура окр. среды, °C', min_value=0,
                                      initial=150, widget=forms.TextInput(attrs={'class': "form-control form-control-sm"}))
    temp_bottom_1 = forms.FloatField(label='Температура поверхности, сек', min_value=-73,
                                     initial=1, widget=forms.TextInput(attrs={'class': "form-control form-control-sm"}))
    thermal_coef_1_bottom = forms.FloatField(label='Коэф. теплопередачи с поверхностью, ', min_value=0,
                                             initial=150, widget=forms.TextInput(attrs={'class': "form-control form-control-sm"}))

