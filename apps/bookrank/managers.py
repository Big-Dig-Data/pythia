from datetime import timedelta

from django.conf import settings
from django.db.models import (
    Manager,
    Case,
    When,
    Sum,
    CharField,
    Count,
    Value as V,
    Q,
    QuerySet,
    FloatField,
    F,
    OuterRef,
    Subquery,
    DateField,
)
from django.db.models.functions import Coalesce, TruncYear, Least
from django.utils import timezone
from mptt.managers import TreeManager, TreeQuerySet

from core.logic.query import prefix_query_filter

DAYS_IN_YR = 365


class BaseScoresQuerySet(QuerySet):
    works_prefix = ''

    def scores_for_last_two_yrs(self):
        b4_12_mo = timezone.now() - timedelta(days=DAYS_IN_YR)
        b4_24_mo = b4_12_mo - timedelta(days=DAYS_IN_YR)
        past_yr_filter = Q(**{f'{self.works_prefix}workhit__date__gte': b4_12_mo})
        yr_b4_filter = Q(**{f'{self.works_prefix}workhit__date__gte': b4_24_mo}) & Q(
            **{f'{self.works_prefix}workhit__date__lt': b4_12_mo}
        )
        return self.annotate(
            annotated_score_past_yr=Coalesce(
                Sum(f'{self.works_prefix}workhit__value', filter=past_yr_filter), 0
            ),
            annotated_score_yr_b4=Coalesce(
                Sum(f'{self.works_prefix}workhit__value', filter=yr_b4_filter), 0
            ),
        )

    def annotate_absolute_growth(self):
        qs = self.scores_for_last_two_yrs()
        return qs.annotate(
            annotated_absolute_growth=F('annotated_score_past_yr') - F('annotated_score_yr_b4')
        )

    def annotate_relative_growth(self):
        qs = self.annotate_absolute_growth()
        return qs.annotate(
            annotated_relative_growth=Case(
                When(annotated_score_yr_b4=0, then=None),
                default=1.0 * F('annotated_absolute_growth') / F('annotated_score_yr_b4'),
                output_field=FloatField(),
            )
        )


class WorkQuerySet(BaseScoresQuerySet):
    def annotate_acquisition_date(self):
        copies_model = self.model._meta.get_field('copies').related_model
        copies = (
            copies_model.objects.filter(work=OuterRef('pk'))
            .order_by(F('acquisition_date').asc(nulls_last=True))
            .values('acquisition_date')[:1]
        )
        hits_model = self.model._meta.get_field('workhit').related_model
        hits = (
            hits_model.objects.filter(work=OuterRef('pk'))
            .order_by(F('date').asc(nulls_last=True))
            .values('date')[:1]
        )
        return (
            self.model.objects.annotate(
                first_copy_acq_date=Subquery(copies, output_field=DateField()),
                first_loan_date=Subquery(hits, output_field=DateField()),
            )
            .annotate(first_copy_loan_date=Least('first_copy_acq_date', 'first_loan_date'))
            .annotate(
                annotated_acquisition_date=Case(
                    When(first_copy_loan_date=None, then=F('catalog_date')),
                    default=F('first_copy_loan_date'),
                    output_field=DateField(),
                )
            )
        )

    def annotate_score(self, score_type='full_score', hit_date_filter=None, low_level=False):
        hit_filter = Q()
        qs = self
        if score_type == 'acquisition_score':
            date_field = 'acquisition_date'
            if low_level:
                qs = qs.annotate_acquisition_date()
                date_field = 'annotated_acquisition_date'
            hit_filter = Q(workhit__date__lte=F(date_field) + timedelta(days=365))
        elif hit_date_filter:
            hit_filter = Q(**prefix_query_filter(hit_date_filter, 'workhit__'))
        return qs.annotate(score=Coalesce(Sum('workhit__value', filter=hit_filter), 0))

    def new_works_acquisition_score(self):
        b4_24_mo = timezone.now() - timedelta(days=2 * DAYS_IN_YR)
        new_works_filter = Q(**{f'{self.works_prefix}acquisition_date__gte': b4_24_mo})
        score_filter = Q(
            **{
                f'{self.works_prefix}workhit__date__lte': F(f'{self.works_prefix}acquisition_date')
                + timedelta(days=DAYS_IN_YR)
            }
        )
        return self.annotate(
            new_works_acquisition_score=(
                Coalesce(
                    Sum(
                        f'{self.works_prefix}workhit__value', filter=new_works_filter & score_filter
                    ),
                    0,
                )
            )
        )

    def acquisition_score_summary(self, low_level=False):
        if low_level:
            qs = self.annotate_acquisition_date().annotate(
                catalog_year=TruncYear('annotated_acquisition_date')
            )
        else:
            qs = self.annotate(catalog_year=TruncYear('acquisition_date'))
        return (
            qs.values('catalog_year')
            .annotate(
                acquisition_score_sum=Sum('acquisition_score'),
                work_count=Count('pk', distinct=True),
            )
            .values('catalog_year', 'acquisition_score_sum', 'work_count')
            .order_by(F('catalog_year').desc(nulls_last=True))
        )


class ETQuerySet(BaseScoresQuerySet):
    works_prefix = 'works__'


class SubjectCategoryQuerySet(TreeQuerySet, ETQuerySet):
    def annotate_root_node(self):
        schema_roots = self.model.objects.filter(
            uid__in=[f'{schema.upper()}-ROOT' for schema in settings.SUBJECT_SCHEMAS]
        )
        # in the following, we not only annotate but also filter because we do not want
        # any categories which are not configured in settings to appear in the result
        return self.annotate(
            root_node=Case(
                *[When(tree_id=schema.tree_id, then=V(schema.name)) for schema in schema_roots],
                output_field=CharField(),
            )
        ).filter(tree_id__in=[schema.tree_id for schema in schema_roots])


class SubjectCategoryManager(Manager.from_queryset(SubjectCategoryQuerySet), TreeManager):
    pass


WorkManager = Manager.from_queryset(WorkQuerySet)
ETManager = Manager.from_queryset(ETQuerySet)
