from __future__ import unicode_literals

from django.db import models
from django.conf import settings

from base.models import *
from infoGatherer.models import Personal_Information


class StatementHistory(BaseModel):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)

class Statement(BaseModel):
    statementHistory = models.ForeignKey(StatementHistory)
    patient = models.ForeignKey(Personal_Information)
    balance = models.DecimalField(**BASE_DECIMAL)
    url = models.SlugField(max_length=128)
