from __future__ import unicode_literals

from django.conf import settings

from base.models import *


class Notes(BaseModel):
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    desc = models.CharField(max_length=255)
