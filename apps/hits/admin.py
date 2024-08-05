from django.contrib import admin
from django.db.models import Sum

from . import models


@admin.register(models.WorkHit)
class WorkHitAdmin(admin.ModelAdmin):

    list_display = ['work', 'date', 'typ', 'value']
    list_select_related = ['work', 'typ']
    search_fields = ['work__name', 'typ__name', 'typ__slug']


@admin.register(models.HitType)
class HitTypeAdmin(admin.ModelAdmin):

    list_display = ['slug', 'name', 'work_hit_count', 'work_unique_targets', 'work_hit_sum']
    search_fields = ['name', 'slug']

    def work_hit_count(self, hit_type: models.HitType):
        return hit_type.workhit_set.all().count()

    def work_unique_targets(self, hit_type: models.HitType):
        return hit_type.workhit_set.all().values('work').distinct('work').count()

    def work_hit_sum(self, hit_type: models.HitType):
        return hit_type.workhit_set.all().aggregate(hit_sum=Sum('value'))['hit_sum']
