from django import forms


class Forming(forms.Form):
    tube_thickness = forms.FloatField(label='Толщина стенки трубы, мм')
    tube_radius = forms.IntegerField(label='Радиус трубы, мм')
