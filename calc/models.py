from dataclasses import dataclass
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
        return f'{self.name}, {self.thickness} мм'


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


@dataclass
class PreparedData:
    thickness: float
    point_layers: int
    temp_ini: float
    form: int
    time_in_zones: List[float]
    time_step: float
    k2: List[float]
    temp_e2: List[float]
    k1: List[float] = 0
    temp_e1: List[float] = 0
    material_data: "ThermalProps" = None
