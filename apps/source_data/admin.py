from django.contrib import admin

from .models import DataSource, DataRecord


@admin.register(DataRecord)
class DataRecordAdmin(admin.ModelAdmin):

    list_display = ['ssid', 'isbn13', 'title', 'source']
    list_filter = ['source']
    search_fields = ['ssid', 'title', 'isbn13']


@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):

    list_display = ['slug', 'data_format', 'description']
