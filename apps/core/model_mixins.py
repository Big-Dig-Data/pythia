from django.db import models
from django.utils import timezone


class CreatedUpdatedMixin(models.Model):
    """
    Simple mixin for storing created and updated dates
    """

    created = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
