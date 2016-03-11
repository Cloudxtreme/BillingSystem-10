from __future__ import unicode_literals

from django.db import models


from base.models import BaseModel
from infoGatherer.models import (Personal_Information, Payer)


class Claim(BaseModel):
    patient = models.ForeignKey(Personal_Information)
    payer = models.ForeignKey(Payer)
    charge = models.DecimalField(max_digits=30, decimal_places=2)
