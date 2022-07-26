from dataclasses import dataclass, field
from typing import List

from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.
from django.utils.text import slugify


class TubeForming(models.Model):
    name = models.CharField(max_length=100, null=False)
    material_test_date = models.DateField()
    thickness = models.FloatField(null=False)
    tension_data = ArrayField(ArrayField(models.FloatField(), size=2), null=False)
    slug = models.SlugField(default='slug', max_length=100, unique=True, null=False)

    def save(self, *args, **kwargs):
        create_slug = self.name + '-' + str(self.thickness).replace('.', '-')
        self.slug = slugify(create_slug)
        super(TubeForming, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.name.upper()}, {self.thickness} mm'


class ChemistryThermal(models.Model):
    name = models.CharField(max_length=100, null=False, unique=True)
    Al = models.FloatField(default=0, null=False)
    Cr = models.FloatField(default=0, null=False)
    Cu = models.FloatField(default=0, null=False)
    Mn = models.FloatField(default=0, null=False)
    Mo = models.FloatField(default=0, null=False)
    Nb = models.FloatField(default=0, null=False)
    Ni = models.FloatField(default=0, null=False)
    Si = models.FloatField(default=0, null=False)
    Ti = models.FloatField(default=0, null=False)
    V = models.FloatField(default=0, null=False)
    W = models.FloatField(default=0, null=False)
    C = models.FloatField(default=0, null=False)
    N = models.FloatField(default=0, null=False)
    P = models.FloatField(default=0, null=False)
    S = models.FloatField(default=0, null=False)

    def __str__(self):
        return f'{self.name}'


class ThermalProps(models.Model):
    name = models.CharField(max_length=100, null=False)
    cooling = models.BooleanField(default=False, null=False)
    conductivity = ArrayField(ArrayField(models.FloatField(), size=2), null=False)
    density = ArrayField(ArrayField(models.FloatField(), size=2), null=False)
    specific_heat = ArrayField(ArrayField(models.FloatField(), size=2), null=False)
    chemistry = models.ForeignKey(ChemistryThermal, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{self.name}'


class CalculatedResults(models.Model):

    created_at = models.DateTimeField(null=False)
    expiration_date = models.DateTimeField(null=False)

    steel_grade_name = models.CharField(max_length=100, null=False)
    steel_grade_id_chemistry = models.ForeignKey(ChemistryThermal, on_delete=models.CASCADE, null=False)
    steel_grade_id_prop = models.ForeignKey(ThermalProps, on_delete=models.CASCADE, null=False)

    geometry = models.IntegerField(null=False)
    thickness = models.FloatField(null=False)
    thickness_points = ArrayField(models.FloatField(), null=False, default=list)
    initial_temperature = models.FloatField(null=False)
    zones_number = models.IntegerField(null=False)
    time_in_zones = ArrayField(models.FloatField(), null=False)
    temp_in_zones = ArrayField(models.FloatField(), null=False)
    coef_in_zones = ArrayField(models.FloatField(), null=False)
    temp_in_zones_bottom = ArrayField(models.FloatField(), null=True)
    coef_in_zones_bottom = ArrayField(models.FloatField(), null=True)
    thickness_layers = models.IntegerField(null=False)
    time_step = models.FloatField(null=False)

    result_zones = ArrayField(ArrayField(models.FloatField()), null=False)

    result_time = ArrayField(ArrayField(models.FloatField()), null=False)
    result_temperature = ArrayField(ArrayField(models.FloatField()), null=False)
    result_change_rate = ArrayField(ArrayField(models.FloatField()), null=False)


@dataclass
class PreparedData:
    thickness: float
    point_layers: int
    temp_ini: float
    form: int
    time_step: float = 0.1
    time_in_zones: List[float] = field(default_factory=list)
    k2: List[float] = field(default_factory=list)
    temp_e2: List[float] = field(default_factory=list)
    k1: List[float] = field(default_factory=list)
    temp_e1: List[float] = field(default_factory=list)
    material_data: "ThermalProps" = None
