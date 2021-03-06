# Generated by Django 4.0.4 on 2022-05-23 13:50

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calc', '0008_alter_calculatedresults_thickness_points'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calculatedresults',
            name='result_change_rate',
            field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(), size=None), size=None),
        ),
        migrations.AlterField(
            model_name='calculatedresults',
            name='result_temperature',
            field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(), size=None), size=None),
        ),
        migrations.AlterField(
            model_name='calculatedresults',
            name='result_time',
            field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(), size=None), size=None),
        ),
    ]
