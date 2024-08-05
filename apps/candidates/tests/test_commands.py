import pytest
from django.core.management import call_command
from django.utils.timezone import now

from candidates.models import Candidate
from source_data.models import DataRecord

THEMA_CREATE_FILE = 'apps/bookrank/tests/data/thema_cats.json'
THEMA_UIDS = [['JMA'], ['JM'], ['J'], ['JMA']]


@pytest.mark.django_db()
class TestSyncCandidatesToDataRecords:
    def test_command(self, work_set, data_records, isbn):
        call_command('sync_candidates_to_data_records', '--disable-transactions', work_set.name)
        assert Candidate.objects.count() == data_records.count()
        record = DataRecord.objects.get(isbn13=isbn)
        candidate = record.candidate
        assert record.isbn13 == candidate.isbn
        candidate_authors = list(candidate.authors.all())
        candidate_langs = list(candidate.languages.all())
        assert candidate_authors
        assert candidate_langs
        assert len(candidate_authors) == 1
        assert candidate_authors[0].name == 'Candidates, Test Author'
        assert len(candidate_langs) == 1
        assert candidate_langs[0].name == 'candidates_test_lang'

    def test_duplicated_isbns(self, work_set, data_records):
        assert DataRecord.objects.count() == len(data_records)
        first_record = DataRecord.objects.get(pk=data_records[0].pk)
        # create a second copy of the first record
        first_record.id = None
        first_record.ssid = '11223344'
        first_record.save()
        assert DataRecord.objects.count() == len(data_records) + 1
        call_command('sync_candidates_to_data_records', '--disable-transactions', work_set.name)
        assert Candidate.objects.count() == data_records.count()
        assert (
            DataRecord.objects.filter(isbn13=first_record.isbn13).count() == 2
        ), 'two data records for the offending ISBN'
        assert (
            Candidate.objects.filter(isbn=first_record.isbn13).count() == 1
        ), 'only one candidate for the duplicated ISBN'

    def test_old_candidates_cleanup(self, work_set, data_records):
        call_command('sync_candidates_to_data_records', '--disable-transactions', work_set.name)
        assert DataRecord.objects.count() == len(data_records)
        # create a second copy of the first record with newer timestamp
        first_record = DataRecord.objects.get(pk=data_records[0].pk)  # type: DataRecord
        fr_raw_data = first_record.raw_data
        first_record.id = None
        first_record.ssid = '11223344'
        first_record.timestamp = now()
        first_record.raw_data = fr_raw_data
        first_record.save()
        fr_raw_data.id = None
        fr_raw_data.record = first_record
        fr_raw_data.save()
        assert DataRecord.objects.count() == len(data_records) + 1
        # sync using the new version
        call_command('sync_candidates_to_data_records', '--disable-transactions', work_set.name)
        assert (
            DataRecord.objects.filter(isbn13=first_record.isbn13).count() == 2
        ), 'two data records for the offending ISBN'
        assert (
            Candidate.objects.filter(isbn=first_record.isbn13).count() == 1
        ), 'only one candidate for the duplicated ISBN'
        candidate = Candidate.objects.get(isbn=first_record.isbn13)
        assert candidate.data_record == first_record, 'newer version is the candidate now'


@pytest.mark.django_db()
class TestCategorizeCandidatesByThema:
    def test_command(self, work_set, candidates):
        call_command('make_thema_tree', work_set, THEMA_CREATE_FILE)
        call_command('categorize_candidates_by_thema', work_set)
        for i, candidate in enumerate(candidates[1:]):
            assert list(candidate.subjects.values_list('uid', flat=True)) == THEMA_UIDS[i]
        assert Candidate.objects.filter(subjects__isnull=True).count() == 1
        assert Candidate.objects.filter(subjects__isnull=False).count() == 4
