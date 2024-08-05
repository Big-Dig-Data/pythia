import csv
import json
from urllib.parse import parse_qs

from django.db.models import OuterRef, Exists, Q, prefetch_related_objects
from django.http import StreamingHttpResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from bookrank.views import BaseDataTableViewSet
from . import models
from . import serializers
from .models import Candidate

DEFAULT_SETTINGS_OBJ = {
    'filters': {},
    'scoreYearIdx': 5,
    'weights': {'authors': 1, 'publisher': 1, 'languages': 1, 'subjects': 1},
    'displayFilters': {'showUnreviewed': True, 'showLiked': True, 'showDisliked': True},
    'ordering': {'sortBy': ["score"], 'sortDesc': [True]},
    'formats': [],
}


class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """

    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


class CandidateViewSet(BaseDataTableViewSet):
    queryset = models.Candidate.objects.select_related('publisher', 'agent').prefetch_related(
        'authors', 'languages', 'subjects'
    )
    serializer_class = serializers.CandidateSerializer
    http_method_names = ['get', 'post']

    search_cols = ('isbn', 'title', 'authors__name', 'publisher__name', 'subjects__name')
    display_filters = [
        ('show_unreviewed', Q(liked=False) & Q(disliked=False)),
        ('show_liked', Q(liked=True)),
        ('show_disliked', Q(disliked=True)),
    ]
    format_filters_map = {
        'printed': lambda qs: qs.exclude(product_format__startswith='B'),
        'unspecified': lambda qs: qs.exclude(product_format=''),
        'other': lambda qs: qs.filter(Q(product_format='') | Q(product_format__startswith='B')),
    }

    csv_headers = ['ISBN', 'Title', 'Languages', 'Authors', 'Publishers', 'Subjects']

    def initialize_request(self, request, *args, **kwargs):
        # hacky solution - extract token from url query string and set auth header manually
        if request.META['PATH_INFO'].endswith('export/'):
            q_dict = parse_qs(request.META['QUERY_STRING'])
            if token := q_dict.get('t', []):
                request.META['HTTP_AUTHORIZATION'] = f'Token {token[0]}'
        return super().initialize_request(request, *args, **kwargs)

    def get_queryset(self):
        qs = self.queryset
        if self.request.query_params.get('works_filter', 0) == '1':
            qs = qs.exclude(matched_works__isnull=False)

        if format_filters := self.request.query_params.getlist('formats[]'):
            for f in self.format_filters_map.keys():
                if f not in format_filters:
                    qs = self.format_filters_map[f](qs)

        if (yop_from := self.request.query_params.get('yop_from')) and yop_from.isdigit():
            qs = qs.filter(publication_year__gte=int(yop_from))
        if (yop_to := self.request.query_params.get('yop_to')) and yop_to.isdigit():
            qs = qs.filter(publication_year__lte=int(yop_to))

        liked = self.request.user.bookmarked_candidates.filter(pk=OuterRef('pk'))
        disliked = self.request.user.blacklisted_candidates.filter(pk=OuterRef('pk'))
        qs = qs.annotate(liked=Exists(liked), disliked=Exists(disliked))
        for filter, q in self.display_filters:
            if not self.request.query_params.get(filter, 'true') == 'true':
                qs = qs.exclude(q)

        if self.request.query_params.get('show_score', False):
            year = self.request.query_params.get('score_year')
            weights = json.loads(self.request.query_params.get('weights'))
            weights = {k: float(v) for k, v in weights.items()}
            qs = qs.annotate_score(weights, year, 'normalized')
        return self.apply_filters(qs)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        obj = self.get_object()
        return self.update_liked_status(request, obj, 'bookmarked_by')

    @action(detail=True, methods=['post'])
    def dislike(self, request, pk=None):
        obj = models.Candidate.objects.get(pk=pk)
        return self.update_liked_status(request, obj, 'blacklisted_by')

    @action(detail=False)
    def export(self, request):
        return StreamingHttpResponse(
            self.export_generator(),
            content_type="text/csv",
            headers={'Content-Disposition': 'attachment; filename="candidates.csv"'},
        )

    def export_generator(self, buffer_size=1000):
        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)
        yield writer.writerow(self.csv_headers)
        qs = self.get_queryset()
        buffer = []
        for c in qs.iterator(chunk_size=10_000):
            buffer.append(c)
            if len(buffer) == buffer_size:
                for rec in self.export_buffer(writer, buffer):
                    yield rec
                buffer = []
        for rec in self.export_buffer(writer, buffer):
            yield rec

    def export_buffer(self, writer, records: [Candidate]):
        prefetch_related_objects(records, 'authors', 'languages', 'subjects')
        rows = [
            [
                rec.isbn,
                rec.title,
                '; '.join(x.name for x in rec.languages.all()),
                '; '.join(x.name for x in rec.authors.all()),
                rec.publisher.name,
                '; '.join(x.name for x in rec.subjects.all()),
            ]
            for rec in records
        ]
        for row in rows:
            yield writer.writerow(row)

    def update_liked_status(self, request, obj, prop):
        action_val = request.data.get('action_val')
        if action_val not in ('add', 'remove'):
            raise ValueError('action_val must be ether "add" or "remove"')
        prop = getattr(obj, prop)
        user = request.user
        if action_val == 'add':
            prop.add(user)
        else:
            prop.remove(user)
        return Response(status=status.HTTP_202_ACCEPTED)

    def format_filter(self, q: str) -> dict:
        field, lookup, q_dict = self.get_filter_field_lookup(q)
        if field in ('author', 'language'):
            field += 's'
        elif field == 'psh':
            field = 'subjects'
        return {f'{field}__{lookup}': q_dict['id']}


class CandidatesSettingsViewSet(ModelViewSet):
    serializer_class = serializers.CandidatesSettingsSerializer

    def get_queryset(self):
        # make sure the default profile exists
        obj, _ = models.CandidatesSettings.objects.get_or_create(
            user=self.request.user,
            name='default',
            internal=True,
            defaults={'settings_obj': DEFAULT_SETTINGS_OBJ},
        )
        qs = self.request.user.candidates_settings.all()
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False)
    def default_profile(self, request):
        obj, _ = models.CandidatesSettings.objects.get_or_create(
            user=request.user,
            name='default',
            internal=True,
            defaults={'settings_obj': DEFAULT_SETTINGS_OBJ},
        )
        serializer = self.get_serializer(obj)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
