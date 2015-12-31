# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('infoGatherer', '0027_auto_20151230_1459'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guarantor_information',
            name='city',
            field=models.CharField(default=b'', max_length=128, null=True, blank=True),
        ),
    ]
