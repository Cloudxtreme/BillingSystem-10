# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import localflavor.us.models


class Migration(migrations.Migration):

    dependencies = [
        ('infoGatherer', '0022_insurance_informationauditlogentry_personal_informationauditlogentry'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guarantor_information',
            name='home_phone',
            field=localflavor.us.models.PhoneNumberField(help_text=b'XXX-XXX-XXXX', max_length=20, null=True),
        ),
    ]
