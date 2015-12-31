# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('infoGatherer', '0030_guarantor_information_zip'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='personal_information',
            name='zip',
        ),
        migrations.RemoveField(
            model_name='personal_informationauditlogentry',
            name='zip',
        ),
    ]
