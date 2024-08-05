from datetime import timedelta, date

import pytest
from django.core.management import call_command
from django.db.models import F
from django.utils import timezone

from bookrank.models import SubjectCategory, Work, Language, WorkCopy
from bookrank.tests.fake_data import WorkFactory
from hits.models import WorkHit
from hits.tests.fake_data import WorkHitFactory

THEMA_CREATE_FILE = 'apps/bookrank/tests/data/thema_cats.json'
WORK_TIME_DELTA = 400


@pytest.mark.django_db
class TestSubjectCategoryManager:
    def test_manager(self, work_set):
        call_command('make_thema_tree', work_set, THEMA_CREATE_FILE)
        psh_root, _ = SubjectCategory.objects.get_or_create(
            uid='PSH-ROOT', name='PSH', parent=None, work_set=work_set
        )
        konspekt_root, _ = SubjectCategory.objects.get_or_create(
            uid='KONSPEKT-ROOT', name='KONSPEKT', parent=None, work_set=work_set
        )
        thema_root = SubjectCategory.objects.get(uid='THEMA-ROOT')
        qs = thema_root.get_descendants()
        qs = qs.annotate_root_node()
        assert all(t.root_node == thema_root.name for t in qs)


@pytest.mark.django_db
class TestETManager:
    def setup_models(self):
        call_command('sync_works_with_aleph', 'test', '-a')
        works = list(Work.objects.all())
        for i, work in enumerate(works, start=1):
            work.acquisition_date = timezone.now() - timedelta(days=i * WORK_TIME_DELTA)
        Work.objects.bulk_update(works, ['acquisition_date'])
        WorkHit.objects.create(work=works[0], value=20, date=timezone.now() - timedelta(days=200))
        WorkHit.objects.create(work=works[0], value=20, date=timezone.now() - timedelta(days=200))
        WorkHit.objects.create(work=works[1], value=10, date=timezone.now() - timedelta(days=200))
        WorkHit.objects.create(work=works[1], value=5, date=timezone.now() - timedelta(days=400))
        WorkHit.objects.create(work=works[2], value=5, date=timezone.now() - timedelta(days=200))
        WorkHit.objects.create(work=works[2], value=10, date=timezone.now() - timedelta(days=400))

    def test_annotate_relative_growth(self, aleph_entries):
        self.setup_models()
        lang = Language.objects.annotate_relative_growth().first()
        assert lang.annotated_score_past_yr == 55
        assert lang.annotated_score_yr_b4 == 15
        assert lang.annotated_absolute_growth == 40
        assert lang.annotated_relative_growth == 40 / 15


@pytest.mark.django_db
class TestWorkManager(TestETManager):
    def test_annotate_acquisition_date(self, works):
        works[0].catalog_date = date(2020, 1, 1)
        works[0].save()
        WorkCopy.objects.create(work=works[0], acquisition_date=date(2000, 1, 1))
        WorkHit.objects.create(work=works[0], date=date(2010, 1, 1), value=1)
        w = Work.objects.annotate_acquisition_date().get(pk=works[0].pk)
        assert w.annotated_acquisition_date == date(2000, 1, 1)
        WorkHit.objects.create(work=works[0], date=date(1999, 1, 1), value=1)
        w = Work.objects.annotate_acquisition_date().get(pk=works[0].pk)
        assert w.annotated_acquisition_date == date(1999, 1, 1)
        WorkCopy.objects.all().delete()
        WorkHit.objects.all().delete()
        w = Work.objects.annotate_acquisition_date().get(pk=works[0].pk)
        assert w.annotated_acquisition_date == date(2020, 1, 1)

    def test_annotate_score(self, aleph_entries):
        self.setup_models()
        qs = Work.objects.annotate_score().order_by('-score').values_list('score', flat=True)
        assert list(qs) == [40, 15, 15]

    def test_annotate_relative_growth(self, aleph_entries):
        self.setup_models()
        qs = Work.objects.annotate_relative_growth()
        vals = qs.order_by('-annotated_absolute_growth').values_list(
            'annotated_absolute_growth', flat=True
        )
        assert list(vals) == [40, 5, -5]
        vals = qs.order_by(F('annotated_relative_growth').desc(nulls_last=True)).values_list(
            'annotated_relative_growth', flat=True
        )
        assert list(vals) == [1.0, -0.5, None]

    def test_new_works_acquisition_score(self, aleph_entries):
        self.setup_models()
        qs = Work.objects.new_works_acquisition_score()
        vals = qs.order_by('-new_works_acquisition_score').values_list(
            'new_works_acquisition_score', flat=True
        )
        assert list(vals) == [40, 0, 0]

    @pytest.mark.parametrize(['low_level'], [(True,), (False,)])
    def test_acquisition_score_summary(self, low_level):
        work1 = WorkFactory.create()
        work2 = WorkFactory.create()
        WorkHitFactory.create(date='2020-05-06', value=11, work=work1)
        WorkHitFactory.create(date='2021-01-06', value=19, work=work1)
        WorkHitFactory.create(date='2021-01-06', value=17, work=work2)
        call_command('update_acquisition_score')
        # work1 should have acquisition score = 30; work2 should have 17
        qs = Work.objects.acquisition_score_summary(low_level=low_level)
        assert list(qs) == [
            {'acquisition_score_sum': 17, 'catalog_year': date(2021, 1, 1), 'work_count': 1},
            {'acquisition_score_sum': 30, 'catalog_year': date(2020, 1, 1), 'work_count': 1},
        ]
