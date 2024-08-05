import pytest
from django.utils.timezone import now

from importers.import_base import ImporterRecord
from ..models import DataRecord, RawDataRecord
from ..logic.data_import import sync_data_with_source


@pytest.mark.django_db
class TestImport:
    def test_sync_data_with_source(self, data_source, generate_importer_records):
        assert DataRecord.objects.count() == 0
        sync_data_with_source(generate_importer_records(), data_source)
        assert DataRecord.objects.count() == 3
        assert RawDataRecord.objects.count() == 3

    def test_sync_data_with_source_reimport(self, data_source, importer_records):
        assert DataRecord.objects.count() == 0
        stats = sync_data_with_source((x for x in importer_records), data_source)
        assert DataRecord.objects.count() == 3
        assert RawDataRecord.objects.count() == 3
        assert stats['new ssid created'] == 3
        stats = sync_data_with_source((x for x in importer_records), data_source)
        assert DataRecord.objects.count() == 3, 'still only 3 records'
        assert RawDataRecord.objects.count() == 3, 'still only 3 records'
        assert stats['new ssid created'] == 0
        assert stats['existing record updated'] == 3

    def test_sync_data_with_source_reimport_update(self, data_source, importer_records):
        assert DataRecord.objects.count() == 0
        stats = sync_data_with_source((x for x in importer_records), data_source)
        assert DataRecord.objects.count() == 3
        assert RawDataRecord.objects.count() == 3
        assert stats['new ssid created'] == 3
        record = importer_records[0]  # type: ImporterRecord
        record.timestamp = now()
        stats = sync_data_with_source((x for x in importer_records), data_source)
        assert DataRecord.objects.count() == 4, '1 extra record for new timestamp'
        assert RawDataRecord.objects.count() == 4, '1 extra record for new timestamp'
        assert stats['new version created'] == 1
        assert stats['existing record updated'] == 2
