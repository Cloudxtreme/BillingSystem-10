# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('infoGatherer', '0031_auto_20151230_1543'),
    ]

    operations = [
        migrations.AddField(
            model_name='personal_information',
            name='zip',
            field=models.CharField(default=b'', max_length=5),
        ),
        migrations.AddField(
            model_name='personal_informationauditlogentry',
            name='zip',
            field=models.CharField(default=b'', max_length=5),
        ),
    ]
