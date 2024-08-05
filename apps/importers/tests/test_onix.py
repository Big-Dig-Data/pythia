from datetime import datetime

import pytest
from pytz import UTC

from importers.import_base import ImporterRecord
from importers.onix import ImportOnix21Reference


class TestOnix21Importer:
    def test_file_parsing_1_record(self, test_data_path):
        reader = ImportOnix21Reference(test_data_path('onix/onix_sample_1_book.xml'))
        record = next(reader)
        assert record is not None
        assert isinstance(record, ImporterRecord)
        assert record.title == 'Test Book'
        assert record.isbn == '9780787960186'
        assert record.ssid == '12345678'
        assert record.doi == 'http://doi.org/10.5555/12345678'
        assert record.timestamp == datetime(2019, 3, 22, 21, 26, 33, tzinfo=UTC)
        with pytest.raises(StopIteration):
            next(reader)

    def test_file_parsing_1_record_no_title(self, test_data_path):
        reader = ImportOnix21Reference(test_data_path('onix/onix_sample_1_book_no_title.xml'))
        record = next(reader)
        assert record is not None
        assert isinstance(record, ImporterRecord)
        assert record.title is None
        assert record.isbn == '9780787960186'
        assert record.ssid == '12345678'
        assert record.doi is None
        assert record.timestamp == datetime(2019, 3, 22, 21, 26, 33, tzinfo=UTC)
        with pytest.raises(StopIteration):
            next(reader)

    def test_file_parsing_iterator_interface(self, test_data_path):
        reader = ImportOnix21Reference(test_data_path('onix/onix_sample_1_book.xml'))
        i = 0
        for _rec in reader:
            i += 1
        assert i == 1, 'one record in the file'
