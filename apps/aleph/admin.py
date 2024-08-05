from django.contrib import admin

from . import models


@admin.register(models.AlephEntry)
class AlephEntryAdmin(admin.ModelAdmin):

    pass
