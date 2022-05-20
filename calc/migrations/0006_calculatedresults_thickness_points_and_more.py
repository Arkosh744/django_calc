# Generated by Django 4.0.4 on 2022-05-19 09:38

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calc', '0005_calculatedresults'),
    ]

    operations = [
        migrations.AddField(
            model_name='calculatedresults',
            name='thickness_points',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(), default=[0], size=None),
        ),
        migrations.AlterField(
            model_name='calculatedresults',
            name='result_change_rate',
            field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(), size=None), size=2),
        ),
        migrations.AlterField(
            model_name='calculatedresults',
            name='result_temperature',
            field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(), size=None), size=2),
        ),
        migrations.AlterField(
            model_name='calculatedresults',
            name='result_time',
            field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(), size=None), size=2),
        ),
    ]