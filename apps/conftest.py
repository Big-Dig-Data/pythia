import pytest
from django.core.management import call_command

from bookrank.models import (
    Language,
    Publisher,
    SubjectCategory,
    WorkSet,
    Work,
    Author,
    WorkCategory,
)
from source_data.models import DataRecord
from candidates.models import Candidate


ONIX_SAMPLE = 'apps/candidates/tests/data/onix_sample.xml'
TEST_ISBN = '9783110616231'
WORK_DATA = [
    {
        "uid": "018221798",
        "name": "Aerodynamická senzace :Tatra 77 /",
        "aleph_data": {
            "cat": [
                {"2": "psh", "7": "psh11052", "a": "osobní automobily", "x": "sr"},
                {"2": "psh", "7": "psh11056", "a": "historické automobily", "x": "sr"},
                {"2": "psh", "7": "psh8015", "a": "konstrukce", "x": "ob"},
                {"2": "psh", "7": "psh13733", "a": "jízdní vlastnosti", "x": "sr"},
                {"2": "psh", "7": "psh5132", "a": "historie vědy a techniky", "x": "hi"},
                {"2": "psh", "7": "psh5042", "a": "historie", "x": "hi"},
            ],
            "lcc": [{"a": "H3"}],
            "udc": [{"2": "MRF", "a": "629.331(091)"}, {"2": "MRF", "a": "629.021"}],
            "lang": "cze",
            "title": [{"a": "Aerodynamická senzace :", "b": "Tatra 77 /", "c": "Jan Tuček"}],
            "author": [{"4": "aut", "7": "jk01140318", "a": "Tuček, Jan,", "d": "1953-"}],
        },
    },
    {
        "uid": "018221800",
        "name": "Litening 4i pro české Gripeny /",
        "aleph_data": {
            "cat": [
                {"2": "psh", "7": "psh12261", "a": "vojenská technika", "x": "vv"},
                {"2": "psh", "7": "psh13655", "a": "stíhací letadla", "x": "sr"},
                {"2": "psh", "7": "psh11154", "a": "letadlové systémy", "x": "sr"},
                {"2": "psh", "7": "psh3449", "a": "optické přístroje", "x": "fy"},
                {"2": "psh", "7": "psh1781", "a": "elektronika", "x": "el"},
            ],
            "lcc": [{"a": "BF139"}],
            "udc": [
                {"2": "MRF", "a": "623.74(437.3)"},
                {"2": "MRF", "a": "623.4.05"},
                {"2": "MRF", "a": "623.4.052.5"},
                {"2": "MRF", "a": "621.38"},
            ],
            "lang": "cze",
            "title": [{"a": "Litening 4i pro české Gripeny /", "c": "Tomáš Soušek"}],
            "author": [{"4": "aut", "7": "mzk2006348548", "a": "Soušek, Tomáš,", "d": "1977-"}],
        },
    },
    {
        "uid": "018221787",
        "name": "Aero L-39NG se připravuje ke vzletu",
        "aleph_data": {
            "cat": [
                {"2": "psh", "7": "psh11139", "a": "vojenská letadla", "x": "sr"},
                {"2": "psh", "7": "psh11142", "a": "konstrukce letadel", "x": "sr"},
                {"2": "psh", "7": "psh11165", "a": "letové zkoušky", "x": "sr"},
                {"2": "psh", "7": "psh8092", "a": "vývoj", "x": "ob"},
            ],
            "lcc": [{"a": "BF353", "b": "asdfasdf"}],
            "udc": [
                {"2": "MRF", "a": "623.746.7(437.312)"},
                {"2": "MRF", "a": "629.746.7"},
                {"2": "MRF", "a": "533.6.054"},
            ],
            "lang": "cze",
            "title": [{"a": "Aero L-39NG se připravuje ke vzletu"}],
        },
    },
]


@pytest.fixture()
def work_set():
    ws, _ = WorkSet.objects.get_or_create(name='test')
    return ws


@pytest.fixture()
def works(work_set):
    book_category = WorkCategory.objects.create(name="Book", work_set=work_set)
    out = []
    for work_data in WORK_DATA:
        work = Work.objects.create(
            work_set=work_set,
            category=book_category,
            name=work_data['name'],
            uid=work_data['uid'],
            extra_data={'aleph': work_data['aleph_data']},
        )
        out.append(work)
    return out


@pytest.fixture()
def data_records():
    call_command('ingest_onix2', 'test', '-c', ONIX_SAMPLE)
    return DataRecord.objects.all()


@pytest.fixture()
def isbn():
    return TEST_ISBN


@pytest.fixture()
def candidates(data_records, work_set):
    call_command('sync_candidates_to_data_records', '--disable-transactions', work_set.name)
    return Candidate.objects.all().order_by('pk')


@pytest.fixture()
def candidate(data_records):
    return Candidate.objects.create(isbn='12345', title='test', data_record=data_records[0])


@pytest.fixture()
def authors(work_set):
    out = [Author(work_set=work_set, name=f'Test Author {i}') for i in range(3)]
    return Author.objects.bulk_create(out)


@pytest.fixture()
def publishers(work_set):
    out = [Publisher(work_set=work_set, name=f'Test Publisher {i}') for i in range(3)]
    return Publisher.objects.bulk_create(out)


@pytest.fixture()
def langs(work_set):
    out = [Language(work_set=work_set, name=f'tl {i}') for i in range(3)]
    return Language.objects.bulk_create(out)


@pytest.fixture()
def subjects(work_set):
    objs = []
    for i in range(3):
        obj = SubjectCategory.objects.create(
            work_set=work_set, name=f'Test Subject {i}', uid=f'test_uid_{i}'
        )
        objs.append(obj)
    return objs
