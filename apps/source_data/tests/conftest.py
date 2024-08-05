from datetime import datetime
from pathlib import Path

import pytest

from importers.import_base import ImporterRecord, DataFormat
from source_data.models import DataSource


@pytest.fixture()
def test_data_path():
    this_dir = Path(__file__).resolve().parent

    def fn(fname: str):
        return this_dir / 'data' / fname

    return fn


@pytest.fixture()
def data_source():
    return DataSource.objects.get_or_create(slug='test', data_format=DataSource.FORMAT_ONIX21)[0]


@pytest.fixture()
def importer_records(faker):
    faker.set_arguments('ssid', {'digits': 6})
    ssid3 = str(faker.random_number(digits=6))
    title3 = faker.sentence()
    text3 = faker.text()
    records = [
        ImporterRecord(
            ssid=str(faker.random_number(digits=6)),
            isbn=faker.isbn13(separator=''),
            title=faker.sentence(),
            doi=f'https://doi.org/10.5555/{faker.md5()}',
            timestamp=datetime(2020, 10, 10, 12, 34, 56),
            raw_data=faker.json(
                data_columns={
                    'ID': 'random_number:ssid',
                    'authors': ['name', 'name'],
                    'text': 'text',
                },
                num_rows=1,
            ),
            raw_data_format=DataFormat.JSON,
        ),
        ImporterRecord(ssid=str(faker.random_number(digits=6)), isbn=faker.isbn13(separator='')),
        ImporterRecord(
            ssid=ssid3,
            title=title3,
            doi=f'https://doi.org/10.5555/{faker.md5()}',
            identifiers={'XYZ': str(faker.random_number(digits=6))},
            timestamp=faker.date_time_this_decade(),
            raw_data=f'<record id="{ssid3}"><title>{title3}</title>'
            f'<abstract>{text3}</abstract></record>',
        ),
    ]
    return records


@pytest.fixture()
def generate_importer_records(importer_records):
    def gen():
        for rec in importer_records:
            yield rec

    return gen


@pytest.fixture()
def importer_records_n(faker):
    def fn(n):
        return [
            ImporterRecord(
                ssid=str(faker.random_number(digits=6)),
                isbn=faker.isbn13(separator=''),
                title=faker.sentence(),
                doi=f'https://doi.org/10.5555/{faker.md5()}',
                timestamp=faker.date_time_this_decade(),
            )
            for _i in range(n)
        ]

    return fn
