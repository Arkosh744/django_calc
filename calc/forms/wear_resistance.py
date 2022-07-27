from django import forms

from calc.models import WearProps


class WearResistForm(forms.Form):
    steel_grades_select = forms.ModelChoiceField(label='Марка стали', queryset=WearProps.objects.all(),
                                                 empty_label='Выберите материал', initial=1,
                                                 widget=forms.Select(attrs={'class': 'form-control-small form-select'}))

    price = forms.FloatField(label='Цена футеровки/покрытия, руб (не обязательно):', min_value=0, initial=0,
                             widget=forms.TextInput(attrs={'class': "form-control form-control-small"}))
    thickness = forms.FloatField(label='Толщина футеровки/покрытия, мм:', min_value=0.01, initial=10,
                                 widget=forms.TextInput(attrs={'class': "form-control form-control-small"}))
    abrasiveness = forms.FloatField(label='Абразивность сыпучей среды * :', min_value=0.0001, initial=0.1,
                                    widget=forms.TextInput(attrs={'class': "form-control form-control-small"}))

    steel_grades_select_2 = forms.ModelChoiceField(label='Марка стали', queryset=WearProps.objects.all(),
                                                   empty_label='Выберите материал', initial=1,
                                                   widget=forms.Select(
                                                       attrs={'class': 'form-control-small form-select'}))
    price_2 = forms.FloatField(label='Цена футеровки/покрытия, руб (не обязательно):', min_value=0, initial=0,
                               widget=forms.TextInput(attrs={'class': "form-control form-control-small"}))
    thickness_2 = forms.FloatField(label='Толщина футеровки/покрытия, мм:', min_value=0.01, initial=10,
                                   widget=forms.TextInput(attrs={'class': "form-control form-control-small"}))
    abrasiveness_2 = forms.FloatField(label='Абразивность сыпучей среды * :', min_value=0.0001, initial=0.1,
                                      widget=forms.TextInput(attrs={'class': "form-control form-control-small"}))
