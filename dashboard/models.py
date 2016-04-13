from __future__ import unicode_literals
from django.db import models
from accounts.models import User
# Create your models here.


class Notes(models.Model):
    author = models.ForeignKey(User)
    desc = models.CharField(max_length=255)