import pytest
from django.core.management import call_command

from ..models import DataRecord, RawDataRecord


@pytest.mark.django_db
class TestIngestOnix2:
    def test_onix_sample_1_book(self, data_source, test_data_path):
        assert DataRecord.objects.count() == 0
        call_command('ingest_onix2', data_source.slug, test_data_path('onix_sample_1_book.xml'))
        assert DataRecord.objects.count() == 1
        assert RawDataRecord.objects.count() == 1
        record = DataRecord.objects.get()
        assert record.isbn13 == '9780787960186'
        assert record.doi == 'http://doi.org/10.5555/12345678'
        assert record.title == 'Test Book'

    def test_onix_sample_1_book_update(self, data_source, test_data_path):
        assert DataRecord.objects.count() == 0
        call_command('ingest_onix2', data_source.slug, test_data_path('onix_sample_1_book.xml'))
        assert DataRecord.objects.count() == 1
        assert RawDataRecord.objects.count() == 1
        record = DataRecord.objects.get()
        assert record.isbn13 == '9780787960186'
        call_command(
            'ingest_onix2', data_source.slug, test_data_path('onix_sample_1_book_updated.xml')
        )
        assert DataRecord.objects.count() == 2
        assert DataRecord.objects.values('ssid').distinct().count() == 1, 'only one ssid'
