from django.db.models import JSONField
from django.db import models
from django.utils.timezone import now

from core.model_mixins import CreatedUpdatedMixin
from importers.import_base import DataFormat


class DataSource(CreatedUpdatedMixin, models.Model):

    FORMAT_MARC21 = 'marc21'
    FORMAT_ONIX21 = 'onix2.1'
    FORMAT_ONIX30 = 'onix3.0'

    FORMAT_CHOICES = (
        (FORMAT_MARC21, FORMAT_MARC21.upper()),
        (FORMAT_ONIX21, FORMAT_ONIX21.upper()),
        (FORMAT_ONIX30, FORMAT_ONIX30.upper()),
    )

    slug = models.SlugField(max_length=32, unique=True)
    data_format = models.CharField(max_length=12, choices=FORMAT_CHOICES)
    description = models.TextField(blank=True)

    def __str__(self):
        return f'{self.slug} ({self.get_data_format_display()})'


class WorkIdentifierMixin(models.Model):

    ssid = models.CharField(max_length=64, help_text='Source specific ID', db_index=True)
    isbn13 = models.CharField(max_length=13, blank=True, db_index=True)
    doi = models.CharField(max_length=256, blank=True)
    other_ids = JSONField(default=dict, blank=True)
    title = models.TextField(blank=True)

    class Meta:
        abstract = True


class DataRecord(WorkIdentifierMixin, CreatedUpdatedMixin, models.Model):

    source = models.ForeignKey(DataSource, on_delete=models.CASCADE)
    extracted_data = JSONField(
        default=dict, blank=True, help_text="Any data of interest extracted from raw data"
    )
    timestamp = models.DateTimeField(
        default=now, help_text='Timestamp extracted from the source data'
    )

    class Meta:
        unique_together = [('ssid', 'source', 'timestamp')]

    def __str__(self):
        return f'{self.source_id}/{self.ssid}'


class RawDataRecord(CreatedUpdatedMixin, models.Model):
    """
    Raw data records can become quite large which can adversely effect query performance
    especially if full table scans are involved.
    To mitigate this, `RawDataRecord` is used as a detached container for the raw data that is
    placed into a separate table and thus does not influence the query performance.
    """

    FMT_CHOICES = ((fmt.value, fmt.value) for fmt in DataFormat)

    data = models.BinaryField(null=True)
    fmt = models.CharField(max_length=4, choices=FMT_CHOICES)
    record = models.OneToOneField(DataRecord, on_delete=models.CASCADE, related_name='raw_data')

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if type(self.data) is str:
            self.data = self.data.encode('utf-8')
        super().save(force_insert, force_update, using, update_fields)
