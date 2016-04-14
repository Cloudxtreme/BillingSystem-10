from __future__ import unicode_literals
from base.models import *
from accounts.models import User
# Create your models here.


class Notes(BaseModel):
    author = models.ForeignKey(User)
    desc = models.CharField(max_length=255)