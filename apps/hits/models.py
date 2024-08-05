from django.db import models

from core.model_mixins import CreatedUpdatedMixin


class HitType(models.Model):

    slug = models.SlugField(max_length=20)
    name = models.CharField(max_length=120)

    def __str__(self):
        return self.name


class WorkHit(CreatedUpdatedMixin, models.Model):

    work = models.ForeignKey('bookrank.Work', on_delete=models.CASCADE)
    value = models.IntegerField(default=1)
    date = models.DateField(
        null=True, blank=True, help_text="May be empty in cases where date is not known"
    )
    typ = models.ForeignKey(HitType, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.work}; {self.date.isoformat()}: {self.value}'
