from __future__ import unicode_literals

from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    created     = models.DateTimeField(editable=False)
    modified    = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        
        self.modified = timezone.now()
        return super(BaseModel, self).save(*args, **kwargs)

    class Meta:
        abstract = True