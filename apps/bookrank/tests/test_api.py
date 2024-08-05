import json
from datetime import timedelta

import pytest
from django.core.management import call_command
from django.utils.timezone import now
from rest_framework.reverse import reverse

from bookrank.models import Work
from bookrank.tests.fake_data import WorkFactory, WorkSetFactory, PublisherFactory, AuthorFactory
from hits.tests.fake_data import WorkHitFactory


@pytest.mark.django_db()
class TestBookrankAPI:
    @pytest.mark.parametrize(
        ['order_by', 'ret_code'],
        [
            ('score', 200),
            ('absolute_growth', 200),
            ('relative_growth', 200),
            ('new_works_acquisition_score', 200),
            ('foo', 400),
            (None, 400),
        ],
    )
    def test_works_top_items(self, admin_client, order_by, ret_code):
        work_set = WorkSetFactory.create()
        WorkFactory.create_batch(5, work_set=work_set)
        attrs = {'order_by': order_by} if order_by else {}
        resp = admin_client.get(reverse('bookrank:works-top-items', args=(work_set.uuid,)), attrs)
        assert resp.status_code == ret_code

    @pytest.mark.parametrize(
        ['order_by', 'desc'],
        [
            ('absolute_growth', True),
            ('absolute_growth', False),
            ('relative_growth', True),
            ('relative_growth', False),
        ],
    )
    def test_works_growth_table(self, admin_client, order_by, desc):
        work_set = WorkSetFactory.create()
        WorkFactory.create_batch(5, work_set=work_set)
        work1, work2, work3, work4, work5 = tuple(Work.objects.all().order_by('pk'))
        today = now().date()
        for work, days_back, value in [
            (work1, 500, 5),
            (work1, 100, 10),
            (work2, 500, 10),
            (work2, 100, 2),
            (work3, 500, 7),
            (work3, 100, 7),
            (work4, 500, 0),
            (work4, 100, 13),
        ]:
            WorkHitFactory.create(work=work, date=today - timedelta(days=days_back), value=value)

        call_command('update_acquisition_score')
        call_command('update_growth_fields')
        expected_values = {
            # work_pk: (abs_growth, rel_growth)
            work1.pk: (5, 1.0),
            work2.pk: (-8, -0.8),
            work3.pk: (0, 0.0),
            work4.pk: (13, None),
            work5.pk: (0, None),
        }

        resp = admin_client.get(
            reverse('bookrank:works_growth_table-list', args=(work_set.uuid,)),
            {'order_by': f'-{order_by}' if desc else order_by},
        )
        assert resp.status_code == 200
        data = resp.json()['results']
        assert len(data) == 5, '5 works'
        for rec in data:
            exp_abs_growth, exp_rel_growth = expected_values[rec['pk']]
            assert exp_abs_growth == rec['absolute_growth']
            assert exp_rel_growth == rec['relative_growth']
        # None values are sorted as lowest. To distinguish between two same Nones we use
        # a value derived from pk there; The pk is used as a second sorting key to properly
        # sort zero values
        field_idx = 0 if order_by == 'absolute_growth' else 1
        assert [rec['pk'] for rec in data] == [
            k
            for k, v in sorted(
                expected_values.items(),
                key=lambda item: (
                    item[1][field_idx] if item[1][field_idx] is not None else (-1e9 + item[0]),
                    item[0],
                ),
                reverse=desc,
            )
        ], 'sorting must match order_by'

    @pytest.mark.parametrize(
        ['filters', 'present'],
        [
            ({}, [True, True, True]),
            ({'author': ['a1']}, [True, False, True]),
            ({'author': ['a2']}, [False, False, True]),
            ({'publisher': ['p1']}, [True, False, False]),
            ({'publisher': ['p2']}, [True, True, False]),
            ({'author': ['a1'], 'publisher': ['p2']}, [True, False, False]),
            ({'author': ['a2'], 'publisher': ['p2']}, [False, False, False]),
        ],
    )
    def test_works_growth_table_with_filters(self, admin_client, filters, present):
        work_set = WorkSetFactory.create()
        p1, p2 = PublisherFactory.create_batch(2, work_set=work_set)
        a1, a2 = AuthorFactory.create_batch(2, work_set=work_set)
        w1 = WorkFactory.create(work_set=work_set, publishers=[p1, p2], authors=[a1])
        w2 = WorkFactory.create(work_set=work_set, publishers=[p2], authors=[])
        w3 = WorkFactory.create(work_set=work_set, publishers=[], authors=[a1, a2])
        today = now().date()
        for work, days_back, value in [
            (w1, 500, 5),
            (w1, 100, 10),
            (w2, 500, 10),
            (w2, 100, 2),
            (w3, 500, 7),
            (w3, 100, 7),
        ]:
            WorkHitFactory.create(work=work, date=today - timedelta(days=days_back), value=value)
        call_command('update_acquisition_score')
        call_command('update_growth_fields')
        expected_values = [
            # (abs_growth, rel_growth)
            (5, 1.0),
            (-8, -0.8),
            (0, 0.0),
        ]
        fs = {}
        local_vars = locals()  # copy of locals() because it will change inside the comprehension
        for key, var_names in filters.items():
            fs[key] = [local_vars[var_name].pk for var_name in var_names]

        resp = admin_client.get(
            reverse('bookrank:works_growth_table-list', args=(work_set.uuid,)),
            {'filters': json.dumps(fs)},
        )
        assert resp.status_code == 200
        data = resp.json()['results']
        assert len(data) == len([x for x in present if x])
