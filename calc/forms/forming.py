from django import forms

from calc.models import TubeForming


class FormingForm(forms.Form):
    tube_thickness = forms.FloatField(label='Толщина стенки трубы, мм')
    tube_radius = forms.IntegerField(label='Радиус трубы, мм')
    material_select = forms.ModelChoiceField(label='Материал трубы', queryset=TubeForming.objects.all())
