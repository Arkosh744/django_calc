from django import forms

from calc.models import TubeForming


class FormingForm(forms.Form):
    tube_thickness = forms.FloatField(label='Толщина стенки трубы, мм', min_value=0, initial=30,
                                      widget=forms.TextInput(attrs={'class': "form-control form-control-small"}))
    tube_radius = forms.IntegerField(label='Радиус трубы, мм', min_value=0, initial=300,
                                     widget=forms.TextInput(attrs={'class': "form-control form-control-small"}))
    material_select = forms.ModelChoiceField(label='Материал трубы', queryset=TubeForming.objects.all(),
                                             empty_label='Выберите материал', initial=3,
                                             widget=forms.Select(attrs={'class': 'form-control-small form-select'}))
