# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('infoGatherer', '0024_locations'),
    ]

    operations = [
        migrations.CreateModel(
            name='Diagnosis_Codes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('diagnosis_name', models.CharField(default=b'', max_length=128)),
                ('diagnosis_code', models.CharField(default=b'', max_length=8)),
            ],
        ),
        migrations.CreateModel(
            name='Procedure_Codes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('procedure_name', models.CharField(default=b'', max_length=128)),
                ('procedure_code', models.IntegerField(default=b'')),
            ],
        ),
        migrations.CreateModel(
            name='Provider',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('provider_name', models.CharField(default=b'', max_length=128)),
                ('tax_id', models.IntegerField(default=b'')),
                ('npi', models.IntegerField(default=b'')),
                ('speciality', models.CharField(default=b'', max_length=128)),
                ('role', models.CharField(default=b'Rendering', max_length=10, choices=[(b'Billing', b'Billing'), (b'Rendering', b'Rendering'), (b'Dual', b'Dual')])),
            ],
        ),
    ]
