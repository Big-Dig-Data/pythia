from collections import Counter
from datetime import date

import pytest

from bookrank.logic.static_score import update_static_scores
from candidates.logic.static_scores import YEARS, update_candidates_static_scores
from hits.models import WorkHit


@pytest.mark.django_db()
class TestCandidateManager:
    def test_update_static_scores(self, works, candidates, authors, publishers, langs, subjects):
        candidates_list = list(candidates[:3])
        zip_iter = zip(works, candidates_list, authors, publishers, langs, subjects)
        for i, (work, candidate, author, pub, lang, subject) in enumerate(zip_iter):
            work.authors.add(author)
            work.publishers.add(pub)
            work.subject_categories.add(subject)
            work.lang = lang
            work.save()
            candidate.authors.add(author)
            candidate.languages.add(lang)
            candidate.subjects.add(subject)
            candidate.publisher = pub
            candidate.save()
            for yr in YEARS:
                WorkHit.objects.create(work=work, date=date(yr, 1, 1), value=5 * (i + 1))
        for candidate in candidates_list:
            assert candidate.static_scores == {}
        update_static_scores(works[0].work_set, Counter())
        stats = update_candidates_static_scores()
        assert stats['updated'] > 0, 'some candidates must be updated'
        assert stats['unchanged'] == 0, 'there should be not unchanged - it is first run'
        for i, year in enumerate(YEARS):
            for j, candidate in enumerate(candidates_list):
                candidate.refresh_from_db()
                # max score is 5 for each YEAR for 1st candidate, 10 for 2nd, 15 for 3rd
                assert candidate.static_scores[f'score_{year}'] == {
                    'authors_score': (5.0 * (j + 1) * (i + 1)),
                    'languages_score': (5.0 * (j + 1) * (i + 1)),
                    'subjects_score': (5.0 * (j + 1) * (i + 1)),
                    'publisher_score': (5.0 * (j + 1) * (i + 1)),
                }
        # test that updating again does update anything
        stats = update_candidates_static_scores()
        assert stats['updated'] == 0, 'nothing should be updated - data has not changed'
        assert stats['unchanged'] > 0, 'all should be unchanged'
