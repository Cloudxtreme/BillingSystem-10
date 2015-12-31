# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('infoGatherer', '0029_remove_guarantor_information_zip'),
    ]

    operations = [
        migrations.AddField(
            model_name='guarantor_information',
            name='zip',
            field=models.CharField(default=b'', max_length=5, null=True, blank=True),
        ),
    ]
