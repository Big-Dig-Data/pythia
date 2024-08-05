import json
from datetime import date, timedelta

import pytest
from django.core.management import call_command
from django.urls import reverse
from django.utils.timezone import now

from bookrank.logic.static_score import update_static_scores, update_growth_fields
from bookrank.models import Publisher, SubjectCategory, Work, Author, AuthorWork
from bookrank.tests.fake_data import (
    WorkSetFactory,
    WorkFactory,
    WorkCopyFactory,
    AuthorFactory,
    PublisherFactory,
)
from candidates.models import Candidate
from candidates.tests.fake_data import CandidateFactory
from hits.models import WorkHit, HitType
from hits.tests.fake_data import WorkHitFactory

THEMA_CREATE_FILE = 'apps/bookrank/tests/data/thema_cats.json'


@pytest.mark.django_db()
class TestWorkViewSet:
    def test_relative_acquisition_score_summary(self, works, admin_client):
        works[0].catalog_date = date(2019, 1, 2)
        works[1].catalog_date = date(2019, 1, 2)
        works[2].catalog_date = date(2020, 1, 2)
        Work.objects.bulk_update(works, ['catalog_date'])
        WorkHit.objects.create(work=works[0], date=date(2019, 2, 2), value=2)
        WorkHit.objects.create(work=works[1], date=date(2019, 2, 2), value=4)
        WorkHit.objects.create(work=works[2], date=date(2020, 2, 2), value=2)
        call_command('update_acquisition_score', works[0].work_set.name)
        resp = admin_client.get(
            reverse(
                'bookrank:works-relative_acquisition_score_summary', args=[works[0].work_set.uuid]
            )
        )
        assert resp.status_code == 200
        # for 2019 it is (4 + 2) / 2 = 3, for 2020 it is 2 / 1 = 2
        assert resp.data == [
            {'catalog_year': date(2019, 1, 1), 'acquisition_score_sum': 3},
            {'catalog_year': date(2020, 1, 1), 'acquisition_score_sum': 2},
        ]

    def test_list(self, admin_client):
        work_set = WorkSetFactory.create()
        works = WorkFactory.create_batch(10, work_set=work_set)
        resp = admin_client.get(reverse('bookrank:works-list', args=(work_set.uuid,)))
        assert resp.status_code == 200
        assert len(resp.json()['results']) == 10
        assert {w.uid for w in works} == {rec['uid'] for rec in resp.json()['results']}

    def test_copies(self, admin_client):
        work_set = WorkSetFactory.create()
        work = WorkFactory.create(work_set=work_set)
        WorkCopyFactory.create_batch(5, work=work)
        resp = admin_client.get(reverse('bookrank:works-copies', args=(work_set.uuid, work.pk)))
        assert resp.status_code == 200
        assert resp.json()['total_num_copies'] == 5

    def test_fake_data(self):
        work_set = WorkSetFactory.create()
        assert Author.objects.count() == 0
        WorkFactory.create_batch(10, work_set=work_set)
        assert Work.objects.count() == 10
        assert Author.objects.count() > 0, "authors are also created by the WorkFactory"
        old_aw_count = AuthorWork.objects.count()
        authors = AuthorFactory.create_batch(3)
        # test explicitly provided list of authors is properly used by the factory
        work = WorkFactory.create(work_set=work_set, authors=authors)
        assert AuthorWork.objects.count() == old_aw_count + 3
        assert work.authors.count() == 3
        assert {a.pk for a in work.authors.all()} == {a.pk for a in authors}


@pytest.mark.django_db
class TestFullSubjectTreeView:
    def test_view_no_data(self, work_set, admin_client):
        call_command('make_thema_tree', work_set, THEMA_CREATE_FILE)
        thema_root = SubjectCategory.objects.get(uid='THEMA-ROOT')
        resp = admin_client.get(
            reverse('bookrank:full_subject_tree', args=[work_set.uuid, thema_root.uid])
        )
        qs = thema_root.get_descendants().order_by('uid')
        assert resp.status_code == 200
        assert resp.json() == {
            'tree': [
                {
                    'id': qs[0].pk,
                    'uid': qs[0].uid,
                    'name': qs[0].name,
                    'score': 0,
                    'acc_score': 0,
                    'work_count': 0,
                    'acc_work_count': 0,
                    'children': [
                        {
                            'id': qs[1].pk,
                            'uid': qs[1].uid,
                            'name': qs[1].name,
                            'score': 0,
                            'acc_score': 0,
                            'work_count': 0,
                            'acc_work_count': 0,
                            'children': [
                                {
                                    'id': qs[2].pk,
                                    'uid': qs[2].uid,
                                    'score': 0,
                                    'acc_score': 0,
                                    'work_count': 0,
                                    'acc_work_count': 0,
                                    'name': qs[2].name,
                                }
                            ],
                        }
                    ],
                }
            ]
        }

    def test_view_with_works_and_hits(self, admin_client):
        """
        Tests that thema subject tree correctly reports scores in presence of works with hits
        """
        work_set = WorkSetFactory.create()
        # copy of thema with only leters J,P,U
        call_command(
            'make_thema_tree', work_set, 'apps/bookrank/tests/data/thema_test_small_deep.json'
        )
        thema_root = SubjectCategory.objects.get(uid='THEMA-ROOT')
        t1 = SubjectCategory.objects.get(uid="PNN")  # organic chemistry
        t2 = SubjectCategory.objects.get(uid="UMW")  # web programming
        w1 = WorkFactory.create(work_set=work_set, subject_categories=[t1, t2])
        w2 = WorkFactory.create(work_set=work_set, subject_categories=[t1])
        today = now().date()
        for days_back, value in ((400, 2), (200, 1), (100, 3)):
            WorkHitFactory.create(work=w1, value=value, date=today - timedelta(days=days_back))
        for days_back, value in ((400, 10), (100, 5)):
            WorkHitFactory.create(work=w2, value=value, date=today - timedelta(days=days_back))
        update_static_scores(work_set)  # computation uses static scores; we need to update them
        # scores: t1 has w1,w2 => 6+15=21; t2 has w1 => 6
        resp = admin_client.get(
            reverse('bookrank:full_subject_tree', args=[work_set.uuid, thema_root.uid])
        )
        assert resp.status_code == 200
        data = resp.json()['tree']

        def find_recursive(tree, target_id):
            for child in tree:
                if child['id'] == target_id:
                    return child
                if hit := find_recursive(child.get('children', []), target_id):
                    return hit

        t1_rec = find_recursive(data, t1.pk)
        assert t1_rec['score'] == 21
        t2_rec = find_recursive(data, t2.pk)
        assert t2_rec['score'] == 6

    @pytest.mark.parametrize(
        ['candidate_count_filters', 'scores'],
        [
            ({}, [2, 1, 2]),
            ({'authors': ['a1']}, [2, 1, 2]),
            ({'authors': ['a2']}, [1, 1, 1]),
            ({'authors': ['a3']}, [0, 0, 0]),
        ],
    )
    def test_view_with_candidates(self, admin_client, candidate_count_filters, scores):
        """
        Tests that thema subject tree correctly reports number of candidates as score when
        score_type=candidates_count is given
        """
        work_set = WorkSetFactory.create()
        # copy of thema with only leters J,P,U
        call_command(
            'make_thema_tree', work_set, 'apps/bookrank/tests/data/thema_test_small_deep.json'
        )
        thema_root = SubjectCategory.objects.get(uid='THEMA-ROOT')
        t1 = SubjectCategory.objects.get(uid="JB")
        t2 = SubjectCategory.objects.get(uid="JBC")  # child of JB
        a1 = AuthorFactory.create(work_set=work_set)
        a2 = AuthorFactory.create(work_set=work_set)
        a3 = AuthorFactory.create(work_set=work_set)  # not associated with any candidate
        CandidateFactory.create(subjects=[t1], authors=[a1])
        CandidateFactory.create(subjects=[t2], authors=[a1, a2])
        ccf = {}
        local_vars = locals()  # copy of locals() because it will change inside the comprehension
        for key, var_names in candidate_count_filters.items():
            ccf[key] = [local_vars[var_name].pk for var_name in var_names]

        resp = admin_client.get(
            reverse('bookrank:full_subject_tree', args=[work_set.uuid, thema_root.uid]),
            {'score_type': 'candidates_count', 'candidate_count_filters': json.dumps(ccf)},
        )
        assert resp.status_code == 200
        data = resp.json()['tree']

        def find_recursive(tree, target_id):
            for child in tree:
                if child['id'] == target_id:
                    return child
                if hit := find_recursive(child.get('children', []), target_id):
                    return hit

        t1_rec = find_recursive(data, t1.pk)
        t2_rec = find_recursive(data, t2.pk)
        j_parent = SubjectCategory.objects.get(uid="J")
        j_parent_rec = find_recursive(data, j_parent.pk)
        assert [t1_rec['acc_score'], t2_rec['acc_score'], j_parent_rec['acc_score']] == scores


@pytest.mark.django_db()
class TestETFiltersViewSet:
    def test_list(self, work_set, candidates, admin_client):
        Publisher.objects.create(name='test', work_set=work_set)
        resp = admin_client.get(
            reverse('bookrank:et_filters-list', args=[work_set.uuid, 'publisher'])
            + '?candidates_filter=1'
        )
        assert resp.status_code == 200
        assert Publisher.objects.count() - 1 == len(resp.data['results'])

    def test_show_candidates_count(self, admin_client):
        work_set = WorkSetFactory.create()
        CandidateFactory.create_batch(10)
        assert Author.objects.count() > 0, "Authors should be created with candidates"
        assert Publisher.objects.count() > 0, "Publishers should be created with candidates"
        resp = admin_client.get(
            reverse('bookrank:et_filters-list', args=[work_set.uuid, 'author']),
            {'show_candidates_count': 1},
        )
        assert resp.status_code == 200
        assert len(resp.json()['results']) == Author.objects.count()
        for rec in resp.json()['results']:
            assert rec['candidates_count'] == 1
        # now test with some filters
        c1 = Candidate.objects.all().order_by('pk')[0]
        c1_authors = {a.pk for a in c1.authors.all()}
        resp = admin_client.get(
            reverse('bookrank:et_filters-list', args=[work_set.uuid, 'author']),
            {
                'show_candidates_count': 1,
                'candidate_count_filters': json.dumps({'publisher': [c1.publisher_id]}),
            },
        )
        assert resp.status_code == 200
        data = resp.json()['results']
        assert len(data) == Author.objects.count()
        for rec in data:
            assert rec['candidates_count'] == (1 if rec['pk'] in c1_authors else 0)

    @pytest.mark.parametrize(['score_type'], [('score',), ('growth',)])
    def test_different_scores(self, admin_client, score_type):
        work_set = WorkSetFactory.create()
        a1, a2, a3 = AuthorFactory.create_batch(3, work_set=work_set)
        w1 = WorkFactory.create(work_set=work_set, authors=[a1, a2])
        w2 = WorkFactory.create(work_set=work_set, authors=[a2])
        today = now().date()
        for days_back, value in ((400, 2), (200, 1), (100, 3)):
            WorkHitFactory.create(work=w1, value=value, date=today - timedelta(days=days_back))
        for days_back, value in ((400, 10), (100, 5)):
            WorkHitFactory.create(work=w2, value=value, date=today - timedelta(days=days_back))
        update_static_scores(work_set)  # computation uses static scores; we need to update them
        update_growth_fields(work_set)  # growth score_type uses growth fields as well
        # scores: a1 has w1 => 1+2+3=6; a2 has w1+w2 => 6+10+5=21; a3 has nothing => 0
        # growth: a1 has w1 => 2->4=+1.0; a2 has w1+w2 => 12->9=-0.25; a3 has nothing => None
        resp = admin_client.get(
            reverse('bookrank:et_filters-list', args=[work_set.uuid, 'author']),
            {"score_type": score_type},
        )
        assert resp.status_code == 200
        data = resp.json()['results']
        assert len(data) == 3, '3 authors'
        exp_scores = {
            "score": [(21, a2), (6, a1), (0, a3)],
            "growth": [(1.0, a1), (-0.25, a2), (None, a3)],
        }
        key = 'score' if score_type == 'score' else 'relative_growth'
        for rec, (exp_score, author) in zip(data, exp_scores[score_type]):
            assert rec[key] == exp_score
            assert rec['pk'] == author.pk


@pytest.mark.django_db
class TestWorkDataTableViewSet:
    @pytest.mark.parametrize(
        ['filters', 'lang_filter', 'present'],
        [
            ({}, None, [True, True, True]),
            ({'author': ['a1']}, None, [True, False, True]),
            ({'author': ['a2']}, None, [False, False, True]),
            ({'publisher': ['p1']}, None, [True, False, False]),
            ({'publisher': ['p2']}, None, [True, True, False]),
            ({'author': ['a1'], 'publisher': ['p2']}, None, [True, False, False]),
            ({'author': ['a2'], 'publisher': ['p2']}, None, [False, False, False]),
            ({'publisher': ['p2']}, 'cze', [True, False, False]),
        ],
    )
    def test_work_filters(self, admin_client, filters, present, lang_filter):
        work_set = WorkSetFactory.create()
        p1, p2 = PublisherFactory.create_batch(2, work_set=work_set)
        a1, a2 = AuthorFactory.create_batch(2, work_set=work_set)
        w1 = WorkFactory.create(work_set=work_set, publishers=[p1, p2], authors=[a1])
        w2 = WorkFactory.create(work_set=work_set, publishers=[p2], authors=[], lang__name='cze')
        w3 = WorkFactory.create(work_set=work_set, publishers=[], authors=[a1, a2])
        fs = {}
        local_vars = locals()  # copy of locals() because it will change inside the comprehension
        for key, var_names in filters.items():
            fs[key] = [local_vars[var_name].pk for var_name in var_names]
        other_fs = {}
        if lang_filter:
            other_fs = {'lang': lang_filter}

        resp = admin_client.get(
            reverse('bookrank:works_table-list', args=(work_set.uuid,)),
            {'filters': json.dumps(fs), **other_fs},
        )
        assert resp.status_code == 200
        data = resp.json()['results']
        assert len(data) == len([x for x in present if x])

    def test_interest_chart_works(self, works, authors, admin_client):
        for w in works:
            w.authors.add(authors[0])
        hit_type_1 = HitType.objects.create(slug='hit-type-1', name='Hit type 1')
        hit_type_2 = HitType.objects.create(slug='hit-type-2', name='Hit type 2')
        WorkHit.objects.create(work=works[0], value=3, date='2020-1-1', typ=hit_type_1)
        WorkHit.objects.create(work=works[1], value=4, date='2020-12-31', typ=hit_type_2)
        WorkHit.objects.create(work=works[2], value=5, date='2020-10-31', typ=hit_type_2)
        WorkHit.objects.create(work=works[2], value=6, date='2020-8-31', typ=hit_type_1)
        WorkHit.objects.create(work=works[0], value=6, date='2021-1-1', typ=hit_type_2)
        url = reverse('bookrank:works_table-interest_chart_works', args=[works[0].work_set.uuid])
        resp = admin_client.get(
            url,
            {
                'filters[]': [f'{{"name": "author", "id": "{authors[0].pk}"}}'],
                'lo_bound': '2020-1-1',
                'hi_bound': '2021-1-1',
            },
        )
        assert resp.status_code == 200
        assert resp.data['count'] == 3
        assert list(resp.data['columns']) == ['Hit type 1', 'Hit type 2']
        assert resp.data['results'] == [
            {'pk': works[2].pk, 'name': works[2].name, 'Hit_type_1': 6, 'Hit_type_2': 5},
            {'pk': works[1].pk, 'name': works[1].name, 'Hit_type_1': 0, 'Hit_type_2': 4},
            {'pk': works[0].pk, 'name': works[0].name, 'Hit_type_1': 3, 'Hit_type_2': 0},
        ]
