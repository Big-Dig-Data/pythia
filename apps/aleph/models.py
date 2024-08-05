from django.db.models import JSONField
from django.db import models

from core.model_mixins import CreatedUpdatedMixin


class AlephEntry(CreatedUpdatedMixin, models.Model):

    uid = models.SlugField(max_length=16, primary_key=True)
    raw_data = JSONField(default=list)

    def __str__(self):
        return "AlephEntry: {}".format(self.uid)
