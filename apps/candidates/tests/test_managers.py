from collections import Counter
from datetime import date
import pytest

from bookrank.logic.static_score import YEARS, update_static_scores
from candidates.logic.static_scores import update_candidates_static_scores
from hits.models import WorkHit
from candidates.models import Candidate


WEIGHTS = {'authors': 0.25, 'languages': 0.1, 'subjects': 0.5, 'publisher': 0.2}
SCORE_YEAR = 'all'


@pytest.mark.django_db()
class TestCandidateManager:
    def test_annotate_score_lowlevel(self, works, candidates, authors, publishers, langs, subjects):
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
        update_static_scores(works[0].work_set, Counter())
        candidates_list[-1].authors.add(authors[0])
        qs = Candidate.objects.filter(
            pk__in=[x.pk for x in candidates_list]
        ).annotate_score_lowlevel(WEIGHTS, SCORE_YEAR, 'static')
        cand = qs.get(pk=candidates_list[0].pk)
        assert cand.score == sum(25 * v for v in WEIGHTS.values())
        for k, v in WEIGHTS.items():
            assert getattr(cand, f'{k}_score') == 25 * v
        cand = qs.get(pk=candidates_list[-1].pk)
        assert cand.score == sum(75 * v for v in WEIGHTS.values())
        for k, v in WEIGHTS.items():
            assert getattr(cand, f'{k}_score') == 75 * v

    def test_annotate_score_with_static_scores(
        self, works, candidates, authors, publishers, langs, subjects
    ):
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
        update_static_scores(works[0].work_set, Counter())
        update_candidates_static_scores()
        candidates_list[-1].authors.add(authors[0])
        qs = Candidate.objects.filter(pk__in=[x.pk for x in candidates_list]).annotate_score(
            WEIGHTS, SCORE_YEAR, 'static'
        )
        cand = qs.get(pk=candidates_list[0].pk)
        assert cand.score == sum(25 * v for v in WEIGHTS.values())
        for k, v in WEIGHTS.items():
            assert getattr(cand, f'{k}_score') == 25 * v
        cand = qs.get(pk=candidates_list[-1].pk)
        assert cand.score == sum(75 * v for v in WEIGHTS.values())
        for k, v in WEIGHTS.items():
            assert getattr(cand, f'{k}_score') == 75 * v

    def test_annotate_score_with_static_scores_no_data(self, candidates):
        """
        Test that when the `static_scores` json field is empty, we still get 0 data and not error
        """
        candidate = candidates.annotate_score(WEIGHTS, SCORE_YEAR, 'static')[0]
        for k in WEIGHTS.keys():
            assert getattr(candidate, f'{k}_score') == 0
