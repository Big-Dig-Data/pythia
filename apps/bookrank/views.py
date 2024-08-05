import json
import operator
from datetime import date
from functools import reduce

from django.contrib.postgres.search import TrigramSimilarity
from django.core.exceptions import BadRequest
from django.db.models import (
    F,
    Count,
    Sum,
    Exists,
    OuterRef,
    Q,
    QuerySet,
    Prefetch,
    IntegerField,
    Case,
    When,
)
from django.db.models.functions import Coalesce, TruncYear, Cast
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from candidates.models import Candidate
from hits.logic.request_attrs import date_filter_from_request
from hits.models import HitType
from . import models
from .logic.topics import build_subject_tree
from .models import SubjectCategory
from .serializers import (
    WorkSerializer,
    WorkDetailedSerializer,
    WorkGrowthSerializer,
    WorkSetSerializer,
    AuthorSerializer,
    PublisherSerializer,
    SubjectCategorySerializer,
    OwnerIntitutionSerializer,
    LanguageSerializer,
    WorkCategorySerializer,
)
from .view_mixins import RequestParameterExtractor


# API


class Pagination15(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'


class Pagination100(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'


class WorkSetViewSet(viewsets.ModelViewSet):
    queryset = models.WorkSet.objects.all().annotate(work_count=Count('works', distinct=True))
    serializer_class = WorkSetSerializer
    # permission_classes = []

    # @method_decorator(cache_page(1*60*60))
    # @method_decorator(vary_on_cookie)
    def list(self, *args, **kwargs):
        return super().list(*args, **kwargs)


class WorkViewSet(viewsets.ModelViewSet):
    queryset = models.Work.objects.all()
    serializer_class = WorkDetailedSerializer
    pagination_class = Pagination100

    # noinspection PyUnresolvedReferences
    def get_queryset(self):
        from core import db  # needed to register the ilike lookup

        workset_uuid = self.kwargs.get('workset_pk')
        queryset = models.Work.objects.filter(work_set__uuid=workset_uuid)
        search_string = self.request.query_params.get('q')
        if search_string:
            for word in search_string.split():
                queryset = queryset.filter(name__ilike=word)
        queryset = (
            queryset.select_related('category', 'lang', 'owner_institution')
            .defer('extra_data')
            .prefetch_related(
                'authors',
                Prefetch(
                    'subject_categories', queryset=SubjectCategory.objects.annotate_root_node()
                ),
            )
        )
        if search_string:
            queryset = queryset.annotate(
                similarity=TrigramSimilarity('name', search_string), score=Sum('workhit__value')
            ).order_by('-similarity', F('score').desc(nulls_last=True))
        return queryset

    @action(detail=False)
    def absolute_acquisition_score_summary(self, request, workset_pk=None):
        qs = models.Work.objects.filter(work_set__uuid=workset_pk).acquisition_score_summary()
        # last 20 years
        return Response(reversed(qs[:20]), status=status.HTTP_200_OK)

    @action(detail=False, url_name='relative_acquisition_score_summary')
    def relative_acquisition_score_summary(self, request, workset_pk=None):
        qs = models.Work.objects.filter(work_set__uuid=workset_pk).acquisition_score_summary()
        data = [
            {
                'catalog_year': x['catalog_year'],
                'acquisition_score_sum': x['acquisition_score_sum'] / x['work_count'],
            }
            for x in reversed(qs[:20])
        ]
        return Response(data=data, status=status.HTTP_200_OK)

    def get_object(self):
        pk = self.kwargs.get('pk')
        subjects = models.SubjectCategory.objects.filter(works__pk=pk).annotate_root_node()
        qs = models.Work.objects.prefetch_related(Prefetch('subject_categories', queryset=subjects))
        return get_object_or_404(qs, pk=pk)

    @action(detail=False)
    def top_items(self, request, workset_pk=None):
        date_filter = date_filter_from_request(request)
        qs = models.Work.objects.filter(work_set__uuid=workset_pk)
        metric = request.query_params.get('order_by')

        fields = ['name', 'pk', metric]
        if metric == 'score':
            qs = qs.annotate_score(hit_date_filter=date_filter).order_by(
                F('score').desc(nulls_last=True)
            )
        elif metric == 'new_works_acquisition_score':
            qs = qs.new_works_acquisition_score().order_by(
                F('new_works_acquisition_score').desc(nulls_last=True)
            )
        elif metric == 'absolute_growth':
            fields += ['score_past_yr', 'score_yr_b4']
        elif metric == 'relative_growth':
            fields += ['score_past_yr', 'score_yr_b4']
        else:
            raise BadRequest(f'invalid order_by argument "{metric}"')

        data = qs.values(*fields)[:10]
        return Response(data={'results': data}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def copies(self, request, workset_pk=None, pk=None):
        qs = (
            models.WorkCopy.objects.filter(work__pk=pk)
            .annotate(year=TruncYear('acquisition_date'))
            .values('year')
            .annotate(num_copies=Count('pk'))
        )
        if total_num_copies := sum(x['num_copies'] for x in qs):
            score = models.Work.objects.filter(pk=pk).annotate_score().first().score
            relative_score = score / total_num_copies
        else:
            total_num_copies = 0
            relative_score = None
        return Response(
            data={
                'relative_score': relative_score,
                'total_num_copies': total_num_copies,
                'years': qs,
            },
            status=status.HTTP_200_OK,
        )

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return WorkDetailedSerializer
        return WorkSerializer


class ExplicitTopicViewSet(viewsets.ReadOnlyModelViewSet):

    topic_type_to_model = {
        'author': (models.Author, AuthorSerializer),
        'publisher': (models.Publisher, PublisherSerializer),
        'psh': (models.SubjectCategory, SubjectCategorySerializer),
        'owner': (models.OwnerInstitution, OwnerIntitutionSerializer),
        'work-type': (models.WorkCategory, WorkCategorySerializer),
        'language': (models.Language, LanguageSerializer),
    }
    serializer_class = None
    pagination_class = Pagination100

    def get_queryset(self):
        workset_uuid = self.kwargs.get('workset_pk')
        model, __ = self._model_and_serializer_by_topic_type()
        queryset = model.objects.filter(work_set__uuid=workset_uuid)
        if self.kwargs['topic_type'] == 'psh':
            queryset = queryset.annotate_root_node()
        search_string = self.request.query_params.get('q')
        if search_string:
            for word in search_string.split():
                queryset = queryset.filter(name__icontains=word)
            queryset = queryset.annotate(
                similarity=TrigramSimilarity('name', search_string),
                score=Sum('works__workhit__value'),
            ).order_by('-similarity', F('score').desc(nulls_last=True))
        else:
            # the following is a workaround for a veeery long query produced without this trick
            # in my tests, the original query did not finish in 30 min, while this one takes a
            # few soconds
            # queryset = model.objects.filter(pk__in=queryset)
            queryset = queryset.annotate(score=Sum('works__workhit__value')).order_by(
                F('score').desc(nulls_last=True)
            )
        return queryset

    def get_serializer_class(self):
        __, serializer = self._model_and_serializer_by_topic_type()
        return serializer

    def _model_and_serializer_by_topic_type(self):
        return self.topic_type_to_model[self.kwargs['topic_type']]


class BaseDataTableViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = None
    serializer_class = None
    pagination_class = Pagination100
    search_cols = []

    def get_queryset(self):
        qs = self.queryset
        return self.apply_filters(qs)

    def apply_filters(self, qs: QuerySet):
        if filters := json.loads(self.request.query_params.get('filters', '{}')):
            q_filters = {
                f'{self.filter_field_to_query_field(name)}__in': ids
                for name, ids in filters.items()
            }
            qs = qs.filter(**q_filters).distinct()
        if order_by := self.request.query_params.get('order_by'):
            # we always add pk to order_by to make the sort stable for tests
            if order_by.startswith('-'):
                qs = qs.order_by(F(order_by[1:]).desc(nulls_last=True), '-pk')
            else:
                qs = qs.order_by(F(order_by).asc(nulls_first=True), 'pk')
        if search := self.request.query_params.get('search'):
            q = reduce(
                operator.or_, [Q(**{f'{col}__icontains': search}) for col in self.search_cols]
            )
            qs = qs.filter(q).distinct()
        return qs

    def get_filter_field_lookup(self, q: str) -> tuple:
        q = json.loads(q)
        field = q['name']
        lookup = 'pk'
        if isinstance(q['id'], list):
            lookup = 'pk__in'
        return field, lookup, q

    def format_filter(self, q: str) -> dict:
        field, lookup, q_dict = self.get_filter_field_lookup(q)
        return {f'{field}__{lookup}': q_dict['id']}

    @classmethod
    def filter_field_to_query_field(cls, field: str) -> str:
        if field in ('author', 'language'):
            return field + 's'
        elif field == 'psh':
            return 'subjects'
        return field


class ETFilterViewSet(ExplicitTopicViewSet, BaseDataTableViewSet):
    topic_to_candidate_field = {
        'publisher': 'publisher',
        'language': 'languages',
        'psh': 'subjects',
        'author': 'authors',
    }
    search_cols = ['name']

    def get_queryset(self):
        qs = super().get_queryset()
        score_type = self.request.query_params.get('score_type', 'score')
        assert score_type in ('score', 'growth')
        # if candidates_filter is true; only show those topics with at least one candidate
        if self.request.query_params.get('candidates_filter') == '1':
            field = self.topic_to_candidate_field[self.kwargs['topic_type']]
            candidate_subq = Candidate.objects.filter(**{field: OuterRef('pk')})
            qs = qs.filter(Exists(candidate_subq))
        model, __ = self._model_and_serializer_by_topic_type()
        qs = model.objects.filter(pk__in=qs)
        if score_type == 'growth':
            qs = qs.order_by(F('relative_growth').desc(nulls_last=True))
        else:
            qs = qs.annotate(
                score=Case(
                    When(
                        static_score__has_key='score_all',
                        then=Cast('static_score__score_all', IntegerField()),
                    ),
                    default=0,
                )
            ).order_by('-score')
        return self.apply_filters(qs)

    def get_paginated_response(self, data):
        if self.request.query_params.get('show_candidates_count') == '1':
            field = self.topic_to_candidate_field[self.kwargs['topic_type']]
            for obj in data:
                obj['candidates_count'] = self.get_candidates_count(field, obj['pk'])
        return super().get_paginated_response(data)

    def get_candidates_count(self, field: str, pk: int) -> int:
        initial_filter = {f'{field}__pk': pk}
        # `candidate_count_filters` define filters on topics which candidates must have to be
        # counted in. This is used for example when the user selects a language and only wants to
        # see authors with candidates in the selected language
        filters = json.loads(self.request.query_params.get('candidate_count_filters', '{}'))
        q_filters = {
            f'{self.filter_field_to_query_field(name)}__in': ids
            for name, ids in filters.items()
            if name != self.kwargs['topic_type']
        }
        return Candidate.objects.filter(**initial_filter).filter(**q_filters).distinct().count()


class FullSubjectTreeView(GenericAPIView):
    http_method_names = ['get']

    def get(self, request, workset_uuid, root_node_uid):
        work_set = models.WorkSet.objects.get(uuid=workset_uuid)
        root_node = models.SubjectCategory.objects.get(uid=root_node_uid, work_set=work_set)
        score_type = request.query_params.get('score_type', 'score')
        cand_cnt_filters = request.query_params.get('candidate_count_filters', '{}')
        cand_cnt_filters = self.get_candidates_filters(cand_cnt_filters)
        return Response({'tree': build_subject_tree(root_node, score_type, cand_cnt_filters)})

    @classmethod
    def get_candidates_filters(cls, filters_q) -> dict:
        filters = json.loads(filters_q)
        out = {}
        for field, ids in filters.items():
            if field == 'psh':
                continue
            if field in ('author', 'language'):
                field += 's'
            out[f'candidates__{field}__in'] = ids
        return out


class WorkDataTableViewSet(RequestParameterExtractor, BaseDataTableViewSet):
    serializer_class = WorkDetailedSerializer
    search_cols = [
        'isbn',
        'name',
        'owner_institution__name',
        'publishers__name',
        'authors__name',
        'subject_categories__name',
    ]

    def get_queryset(self):
        qs = models.Work.objects.select_related(
            'category', 'lang', 'owner_institution'
        ).prefetch_related(
            'publishers',
            'authors',
            Prefetch('subject_categories', queryset=SubjectCategory.objects.annotate_root_node()),
        )
        score_type = self.request.query_params.get('score_type', 'full_score')
        qs = qs.filter(work_set__uuid=self.kwargs.get('workset_pk')).annotate_score(
            score_type=score_type
        )
        if catalog_year := self.request.query_params.get('catalog_year'):
            if catalog_year == 'date_missing':
                qs = qs.filter(acquisition_date__isnull=True)
            else:
                catalog_year = int(catalog_year)
                start = date(catalog_year, 1, 1)
                end = date(catalog_year + 1, 1, 1)
                qs = qs.filter(acquisition_date__gte=start, acquisition_date__lt=end)
        work_filters = self._extract_work_filter(self.request)
        qs = self.apply_filters(qs)
        qs = qs.filter(**work_filters)
        return qs

    def get_interest_chart_works_qs(self):
        self.columns = HitType.objects.values_list('name', flat=True)
        self.extra_fields = [c.replace(' ', '_') for c in self.columns]
        lo = self.request.query_params.get('lo_bound')
        hi = self.request.query_params.get('hi_bound')
        annotation = {
            col.replace(' ', '_'): Coalesce(
                Sum(
                    'workhit__value',
                    filter=Q(workhit__date__gte=lo)
                    & Q(workhit__date__lt=hi)
                    & Q(workhit__typ__name=col),
                ),
                0,
            )
            for col in self.columns
        }
        full_score_annotation = {
            'full_score': reduce(operator.add, [F(col) for col in self.extra_fields])
        }
        return (
            models.Work.objects.filter(work_set__uuid=self.kwargs.get('workset_pk'))
            .annotate(**annotation)
            .annotate(**full_score_annotation)
            .filter(full_score__gt=0)
            .order_by('-full_score')
        )

    @action(detail=False, url_name='interest_chart_works')
    def interest_chart_works(self, request, workset_pk=None):
        qs = self.get_interest_chart_works_qs()
        qs = self.apply_filters(qs).values('pk', 'name', *self.extra_fields)
        page = self.paginate_queryset(qs)
        return Response(
            data={'results': page, 'count': qs.count(), 'columns': self.columns},
            status=status.HTTP_200_OK,
        )

    @action(detail=False)
    def catalog_years(self, request, workset_pk=None):
        years = (
            models.Work.objects.filter(acquisition_date__isnull=False)
            .annotate(catalog_year=TruncYear('acquisition_date'))
            .values_list('catalog_year')
            .distinct()
            .order_by(F('catalog_year').desc(nulls_last=True))
        )
        return Response(data=years, status=status.HTTP_200_OK)

    @classmethod
    def filter_field_to_query_field(cls, field: str) -> str:
        if field in ('author', 'language', 'publisher'):
            return field + 's'
        elif field == 'psh':
            return 'subject_categories'
        return field


class WorkGrowthTable(RequestParameterExtractor, BaseDataTableViewSet):
    serializer_class = WorkGrowthSerializer
    queryset = models.Work.objects.all()
    search_cols = [
        'name',
        'lang__name',
        'authors__name',
        'publishers__name',
        'subject_categories__name',
    ]

    def get_queryset(self):
        qs = self.queryset.select_related('lang').prefetch_related(
            'authors', 'publishers', 'subject_categories'
        )
        work_filters = self._extract_work_filter(self.request)
        qs = self.apply_filters(qs)
        qs = qs.filter(**work_filters)
        return qs

    @classmethod
    def filter_field_to_query_field(cls, field: str) -> str:
        if field in ('author', 'language', 'publisher'):
            return field + 's'
        elif field == 'psh':
            return 'subject_categories'
        return field
