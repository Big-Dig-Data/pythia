import csv
from io import StringIO

import pytest

from bookrank.tests.fake_data import WorkSetFactory, WorkFactory
from hits.logic.workhit_data import load_workhits_from_csv
from hits.models import WorkHit
from hits.tests.fake_data import HitTypeFactory


@pytest.mark.django_db
class TestCommands:
    def test_load_workhits_from_csv(self, fs):
        work_set = WorkSetFactory.create()
        works = WorkFactory.create_batch(10, work_set=work_set)
        ht = HitTypeFactory.create()
        content = StringIO()
        writer = csv.writer(content)
        writer.writerow(['id', 'date', 'count'])
        for i, work in enumerate(works):
            writer.writerow([work.uid, '20210101', i + 1])
        fs.create_file('test.csv', contents=content.getvalue())
        load_workhits_from_csv('test.csv', work_set, hit_type=ht)
        assert WorkHit.objects.count() == 10
