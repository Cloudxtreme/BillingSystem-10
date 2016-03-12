from __future__ import unicode_literals

from django.db import models
from django.utils import timezone


# Default size of decimal field on this project (30 digits including 2 decimals)
MAX_DIGITS = 30
DECIMAL_PLACES = 2


class BaseModel(models.Model):
    """
    Abstract class of all models in this project.
    All models must have field to indicate when it is created and last modified.
    django.utils.timezone is prefer to datetime.datetime because it created
    timezone awareness object.
    """
    created     = models.DateTimeField(editable=False)
    modified    = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        
        self.modified = timezone.now()
        return super(BaseModel, self).save(*args, **kwargs)

    class Meta:
        abstract = True