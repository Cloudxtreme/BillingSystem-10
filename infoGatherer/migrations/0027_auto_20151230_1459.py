# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('infoGatherer', '0026_auto_20151230_1458'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guarantor_information',
            name='dob',
            field=models.DateField(null=True, blank=True),
        ),
    ]
