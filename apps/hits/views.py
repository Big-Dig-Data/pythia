from collections import Counter
from datetime import timedelta

from dateutil.relativedelta import relativedelta
from dateutil.utils import today
from django.db.models import Q, Count, F, FloatField
from django.db.models import Sum, Min, Max
from django.db.models.functions import Cast, Coalesce
from django.db.models.functions import TruncMonth, TruncDay, TruncWeek, TruncYear
from rest_framework.generics import get_object_or_404, GenericAPIView
from rest_framework.response import Response

from bookrank.models import WorkSet, Work, Language, OwnerInstitution, WorkCategory
from bookrank.serializers import WorkSerializer, WorkSimpleScoreSerializer
from bookrank.view_mixins import RequestParameterExtractor
from core.exceptions import BadRequestError
from core.logic.query import prefix_query_filter
from core.pagination import SmartPageNumberPagination
from .logic.request_attrs import date_filter_from_request
from .models import WorkHit, HitType


class Pagination20(SmartPageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'


class BaseWorkHitStatsView(RequestParameterExtractor, GenericAPIView):

    pagination_class = Pagination20

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.workset = None
        self.topic_type = None
        self.work_filter = None
        self.add_work_count = False
        self.date_filter = None
        self.hit_type_filter = None

    def _get_total_score(self, request):
        work_filter = prefix_query_filter(self.work_filter, 'work__')
        score = WorkHit.objects.filter(
            **self._extract_hit_type_filter(request),
            **date_filter_from_request(request),
            **work_filter,
        ).aggregate(sum=Sum('value'))
        return score['sum']

    def _get_total_count(self, request):
        count = Work.objects.filter(**self.work_filter).count()
        return count

    def _add_relative_counts(self, request, result):
        total_score = self._get_total_score(request)
        total_count = self._get_total_count(request)
        for rec in result:
            rec['work_count_rel'] = (rec['work_count'] / total_count) if rec['work_count'] else None
            rec['score_rel'] = (rec['score'] / total_score) if rec['score'] else None
        return result


class ExplicitTopicsHitStatsView(BaseWorkHitStatsView):
    growth_metrics = ['absolute_growth', 'relative_growth']

    def get_queryset(self):
        self.date_filter = prefix_query_filter(
            date_filter_from_request(self.request), 'works__workhit__'
        )
        self.hit_type_filter = prefix_query_filter(
            self._extract_hit_type_filter(self.request), 'works__workhit__'
        )
        self.work_filter = self._extract_work_filter(self.request)
        works_filter = prefix_query_filter(self.work_filter, 'works__')
        topic_model = self.topic_type_to_explicit_topic.get(self.topic_type)
        queryset = topic_model.objects.filter(work_set=self.workset, **works_filter).annotate(
            score=Sum(
                'works__workhit__value', filter=Q(**self.date_filter, **self.hit_type_filter)
            ),
            work_count=Count('works', distinct=True),
            ratio=(
                Cast(F('score'), output_field=FloatField())
                / Cast(F('work_count'), output_field=FloatField())
            ),
        )
        if self.topic_type == 'psh':
            queryset = queryset.annotate_root_node()
            if root_node := self.request.query_params.get('root_node'):
                queryset = queryset.filter(root_node=root_node)
        return queryset

    @classmethod
    def _get_order_by(cls, request):
        attr_name = request.query_params.get(cls.ORDER_BY_PARAM, cls.ORDERING_TYPES[0])
        if attr_name not in cls.ORDERING_TYPES:
            raise BadRequestError(
                f'Invalid value "{attr_name}" for {cls.ORDER_BY_PARAM} - '
                f'must be one of {cls.ORDERING_TYPES}'
            )
        return F(cls.ORDERING_TYPES_REMAP[attr_name]).desc(nulls_last=True), attr_name

    # @method_decorator(cache_page(1*60*60))
    def get(self, request, workset_uuid, topic_type):
        self.workset = get_object_or_404(WorkSet.objects.all(), uuid=workset_uuid)
        self.topic_type = topic_type
        order_by, order_attr = self._get_order_by(request)
        fields = ['score', 'pk', 'name', 'work_count', 'ratio']
        if self.topic_type == 'psh':
            fields.append('root_node')
        if order_attr in self.growth_metrics:
            fields += [order_attr, 'score_past_yr', 'score_yr_b4']
        queryset = (
            self.get_queryset()
            .values(*fields)
            .filter(**self._extract_post_aggregation_filter(request))
            .order_by(order_by, 'name')
        )
        paginator = self.pagination_class()
        result = paginator.paginate_queryset(queryset, request)
        self._add_relative_counts(request, result)
        return paginator.get_paginated_response(result)


class ExplicitTopicsHitHistogramView(BaseWorkHitStatsView):

    histogram_bins = [
        (0, 0),
        (1, 1),
        (2, 5),
        (6, 10),
        (11, 20),
        (21, 50),
        (51, 100),
        (101, 200),
        (201, 500),
        (501, 1000),
    ]

    def get_queryset(self):
        self.date_filter = prefix_query_filter(
            date_filter_from_request(self.request), 'works__workhit__'
        )
        self.hit_type_filter = prefix_query_filter(
            self._extract_hit_type_filter(self.request), 'works__workhit__'
        )
        self.work_filter = self._extract_work_filter(self.request)
        works_filter = prefix_query_filter(self.work_filter, 'works__')
        topic_model = self.topic_type_to_explicit_topic.get(self.topic_type)
        queryset = topic_model.objects.filter(work_set=self.workset, **works_filter).annotate(
            score=Coalesce(
                Sum('works__workhit__value', filter=Q(**self.date_filter, **self.hit_type_filter)),
                0,
            )
        )
        if root_node := self.request.query_params.get('root_node'):
            queryset = queryset.annotate_root_node().filter(root_node=root_node)
        return queryset

    def get(self, request, workset_uuid, topic_type):
        self.workset = get_object_or_404(WorkSet.objects.all(), uuid=workset_uuid)
        self.topic_type = topic_type
        queryset = self.get_queryset().values('pk', 'score')
        counter = Counter()
        for rec in queryset:
            counter[rec['score']] += 1
        # here we bin it according to self.histogram_bins
        bin_counter = Counter()
        for hits, count in counter.items():
            for start, end in self.histogram_bins:
                if start <= hits <= end:
                    bin_counter[(start, end)] += count
                    break
            else:
                digits = len(str(hits)) - 1
                unit = 10**digits
                start = unit * ((hits - 1) // unit)
                end = start + unit
                start += 1
                bin_counter[(start, end)] += count

        # objects to return
        def name(a, b):
            if a == b:
                return str(a)
            return f'{a}-{b}'

        data = [
            {'count': count, 'start': start, 'end': end, 'name': name(start, end)}
            for (start, end), count in sorted(bin_counter.items())
        ]
        return Response(data)


class ExplicitTopicWorkStatsView(GenericAPIView):

    model = None

    def get(self, request, workset_uuid):
        if not self.model:
            raise ValueError('You must provide the model attr in a subclass')
        queryset = (
            self.model.objects.filter(work_set__uuid=workset_uuid)
            .annotate(count=Count('works'))
            .values('count', 'pk', 'name')
            .order_by('-count', 'name')[:20]
        )
        return Response(queryset)


class LangWorkStatsView(ExplicitTopicWorkStatsView):

    model = Language


class OwnerInstitutionWorkStatsView(ExplicitTopicWorkStatsView):

    model = OwnerInstitution


class WorkCategoryWorkStatsView(ExplicitTopicWorkStatsView):

    model = WorkCategory


# time related API


class TimePeriodStatsMixin(object):

    META = {'labelMap': {'score': 'Skóre zájmu'}}
    # shift is used to move the center of the data because the trunc function gives all
    # monthly data to the first day of the month
    step_to_params = {
        'year': {
            'trunc': TruncYear,
            'shift': timedelta(days=183),
            'step_name': 'Rok',
            'delta': relativedelta(years=1),
        },
        'month': {
            'trunc': TruncMonth,
            'shift': timedelta(days=15),
            'step_name': 'Měsíc',
            'delta': relativedelta(months=1),
        },
        'week': {
            'trunc': TruncWeek,
            'shift': timedelta(days=3),
            'step_name': 'Týden',
            'delta': relativedelta(weeks=1),
        },
        'day': {
            'trunc': TruncDay,
            'shift': timedelta(days=0),
            'step_name': 'Den',
            'delta': relativedelta(days=1),
        },
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.step = None
        self.params = None
        self.extra = None
        self.label_map = {}
        self.workset = None

    def _extract_step_and_params(self):
        step = self.request.GET.get('step', 'month')
        if step not in self.step_to_params:
            step = 'month'
        self.step = step
        self.params = self.step_to_params[step]


class WorkHitInTimeBaseStatsView(TimePeriodStatsMixin, BaseWorkHitStatsView):
    def get_data_raw(self):
        raise NotImplementedError('must implement in derived classes')

    def get_statistics(self):
        self.date_filter = date_filter_from_request(self.request)
        self.hit_type_filter = self._extract_hit_type_filter(self.request)
        # we create a map of HitTypes, but only those that have at least one hit anywhere in the DB
        hittype_id_to_name = {
            ht.pk: ht.name
            for ht in HitType.objects.annotate(score=Sum('workhit')).filter(score__gt=0)
        }
        trunc = self.params['trunc']
        data = self.get_data_raw()
        # here we add zero data where necessary
        # we use the min and max of the data in the DB, but if there is date_filter,
        # we limit the limits we got
        date_limits = WorkHit.objects.filter(**self.date_filter).aggregate(
            min_unit=trunc(Min('date')), max_unit=trunc(Max('date'))
        )
        last_date = None
        current_data = {}
        shift = self.params['shift']
        date_to_data = {}
        for row in data:
            if not last_date:
                last_date = row['unit']
            if last_date != row['unit']:
                if current_data:
                    date_to_data[last_date] = current_data
                current_data = {}
                last_date = row['unit']
            current_data[row['typ']] = row['score']
        if current_data:
            date_to_data[last_date] = current_data
        # now process the whole date range
        date = date_limits['min_unit']
        max_date = date_limits['max_unit']
        if date is None:
            # there are no hit data
            date = today().replace(day=1)
            max_date = date.replace(year=date.year - 1)
        result = []
        while date <= max_date:
            current_data = date_to_data.get(date, {})
            if 'date' not in current_data:
                current_data['date'] = (date + shift).isoformat()
            if self.step == 'year':
                current_data['date'] = current_data['date'][:4]
            for hittype_id in hittype_id_to_name.keys():
                if hittype_id not in current_data:
                    current_data[hittype_id] = 0
            result.append(current_data)
            date += self.params['delta']
        self.label_map = hittype_id_to_name
        self.extra = {'series': list(hittype_id_to_name.keys())}
        return result


class WorkHitsInTimeStatsView(WorkHitInTimeBaseStatsView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.work_id = None

    def get_data_raw(self):
        trunc = self.params['trunc']
        data = (
            WorkHit.objects.filter(work_id=self.work_id, **self.date_filter, **self.hit_type_filter)
            .annotate(unit=trunc('date'))
            .values('unit', 'typ')
            .annotate(score=Sum('value'))
            .order_by('unit')
            .values('unit', 'score', 'typ')
        )
        return data

    def get(self, request, work_id):
        self.work_id = work_id
        self._extract_step_and_params()
        # we extract stats here because as a side-effect, it will fill out the label_map
        stats = self.get_statistics()
        meta = dict(self.META)
        meta['labelMap'].update({'date': self.params['step_name']})
        meta['labelMap'].update(self.label_map)
        output = {'stats': stats, 'meta': meta}
        if self.extra:
            output['extra'] = self.extra
        return Response(output)


class ExplicitTopicsInTimeStatsView(WorkHitInTimeBaseStatsView):
    def get_data_raw(self):
        self.work_filter = prefix_query_filter(self._extract_work_filter(self.request), 'work__')
        trunc = self.params['trunc']
        data = (
            WorkHit.objects.filter(**self.work_filter, **self.date_filter, **self.hit_type_filter)
            .annotate(unit=trunc('date'))
            .values('unit', 'typ')
            .annotate(score=Sum('value'))
            .order_by('unit')
            .values('unit', 'score', 'typ')
        )
        return data

    def get(self, request):
        self._extract_step_and_params()
        # we extract stats here because as a side-effect, it will fill out the label_map
        stats = self.get_statistics()
        meta = dict(self.META)
        meta['labelMap'].update({'date': self.params['step_name']})
        meta['labelMap'].update(self.label_map)
        output = {'stats': stats, 'meta': meta}
        if self.extra:
            output['extra'] = self.extra
        return Response(output)


class ExplicitTopicsImportantWorksView(BaseWorkHitStatsView):
    def get_queryset(self):
        self.date_filter = prefix_query_filter(date_filter_from_request(self.request), 'workhit__')
        self.hit_type_filter = self._extract_hit_type_filter(self.request)
        self.work_filter = self._extract_work_filter(self.request)
        queryset = (
            Work.objects.filter(work_set=self.workset, **self.work_filter)
            .annotate(
                score=Coalesce(
                    Sum('workhit__value', filter=Q(**self.date_filter, **self.hit_type_filter)), 0
                )
            )
            .order_by(F('score').desc(nulls_last=True))
        )
        return queryset

    def get(self, request, workset_uuid, topic_type):
        self.workset = get_object_or_404(WorkSet.objects.all(), uuid=workset_uuid)
        self.topic_type = topic_type
        # by deferring `extra_data` json field below, we get more than 2x speed-up
        # for some reason, Postgres adds some extra sort into the plan when `extra_data`
        # is included and that makes is slow
        queryset = (
            self.get_queryset()
            .prefetch_related('authors')
            .select_related('category')
            .defer('extra_data')
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = WorkSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = WorkSerializer(queryset, many=True)
        return Response(serializer.data)


class ImportantWorksView(BaseWorkHitStatsView):
    def get_queryset(self):
        self.date_filter = prefix_query_filter(date_filter_from_request(self.request), 'workhit__')
        self.hit_type_filter = self._extract_hit_type_filter(self.request)
        self.work_filter = self._extract_work_filter(self.request)
        queryset = (
            Work.objects.filter(work_set=self.workset, **self.work_filter)
            .annotate(
                score=Coalesce(
                    Sum('workhit__value', filter=Q(**self.date_filter, **self.hit_type_filter)), 0
                )
            )
            .order_by(F('score').desc(nulls_last=True))
        )
        return queryset

    def get(self, request, workset_uuid):
        self.workset = get_object_or_404(WorkSet.objects.all(), uuid=workset_uuid)
        # by deferring `extra_data` json field below, we get more than 2x speed-up
        # for some reason, Postgres adds some extra sort into the plan when `extra_data`
        # is included and that makes is slow
        queryset = self.get_queryset().prefetch_related('authors', 'category').defer('extra_data')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = WorkSimpleScoreSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = WorkSimpleScoreSerializer(queryset, many=True)
        return Response(serializer.data)


class WorkHitsWorkDetailView(GenericAPIView):
    def get(self, request, work_id):
        date_filter = prefix_query_filter(date_filter_from_request(request), 'workhit__')
        data = (
            HitType.objects.all()
            .annotate(
                score=Coalesce(
                    Sum('workhit__value', filter=Q(workhit__work_id=work_id, **date_filter)), 0
                )
            )
            .values('name', 'score')
        )
        return Response(data)
