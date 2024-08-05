from collections import Counter

import pytest

from bookrank.logic.static_score import update_static_scores
from bookrank.tests.fake_data import WorkSetFactory, AuthorFactory, WorkFactory
from hits.tests.fake_data import WorkHitFactory


@pytest.mark.django_db
class TestStaticScores:
    def test_static_score_computation(self):
        work_set = WorkSetFactory.create()
        a1 = AuthorFactory.create(work_set=work_set)
        work1 = WorkFactory.create(work_set=work_set, authors=[a1])
        work2 = WorkFactory.create(work_set=work_set, authors=[a1])
        WorkHitFactory.create(date='2020-05-06', value=11, work=work1)
        WorkHitFactory.create(date='2021-01-06', value=19, work=work1)
        WorkHitFactory.create(date='2021-01-06', value=17, work=work2)
        assert a1.static_score == {}
        stats = Counter()
        update_static_scores(work_set, stats)
        a1.refresh_from_db()
        assert a1.static_score['score_all'] == 47
