# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('infoGatherer', '0028_auto_20151230_1501'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='guarantor_information',
            name='zip',
        ),
    ]
