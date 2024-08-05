from django.contrib import admin

from . import models


@admin.register(models.Work)
class WorkAdmin(admin.ModelAdmin):

    list_display = ['uid', 'name', 'category']
    search_fields = ['name', 'uid']


@admin.register(models.WorkCategory)
class WorkCategoryAdmin(admin.ModelAdmin):

    list_display = ['name']
    search_fields = ['name']


@admin.register(models.WorkSet)
class WorkSetAdmin(admin.ModelAdmin):

    list_display = ['uuid', 'name', 'description', 'work_count']
    search_fields = ['name', 'description', 'uuid']

    def work_count(self, workset: models.WorkSet):
        return workset.works.count()


class ExplicitTopicAdmin(admin.ModelAdmin):

    list_display = ['name', 'pk', 'work_set', 'last_updated']
    list_filter = ['work_set']
    search_fields = ['name']


admin.site.register(models.Author, ExplicitTopicAdmin)
admin.site.register(models.SubjectCategory, ExplicitTopicAdmin)
admin.site.register(models.Language, ExplicitTopicAdmin)
admin.site.register(models.WorkCopy)
