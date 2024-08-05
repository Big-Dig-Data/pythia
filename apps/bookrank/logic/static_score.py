from collections import Counter
from typing import List, Optional
import logging
from datetime import date
from django.db.models import QuerySet, Sum, Q, Count, FloatField, Max
from django.db.models.functions import Cast, Coalesce
from django.db.models.fields.json import KeyTextTransform
from django.conf import settings
from django.db.transaction import atomic
from tqdm import tqdm

from hits.models import WorkHit
from ..models import (
    Author,
    Publisher,
    Language,
    SubjectCategory,
    WorkSet,
    OwnerInstitution,
    WorkCategory,
    Work,
)

logger = logging.getLogger(__name__)

MODELS_TO_UPDATE = (
    (Author, 'authors'),
    (Publisher, 'publishers'),
    (Language, 'lang'),
    (SubjectCategory, 'subject_categories'),
)
YEARS = (2020, 2015, 2010, 2005, 2000)


def make_annotations_dict() -> dict:
    agg_dict = {
        f'score_{yr}': Coalesce(
            Sum('works__workhit__value', filter=Q(works__workhit__date__gte=date(yr, 1, 1))), 0
        )
        for yr in YEARS
    }
    agg_dict['score_all'] = Coalesce(Sum('works__workhit__value'), 0)
    return agg_dict


def get_maximums(qs: QuerySet, field: str) -> dict:
    years = [*YEARS, 'all']
    annotation = {
        f'score_{yr}': Cast(KeyTextTransform(f'score_{yr}', 'static_score'), FloatField())
        for yr in years
    }
    # when getting max for langs, authors and publishers
    # only consider topics connected to candidates
    # same filtering doesn't make sense for subject categories IMO
    if field != 'subject_categories':
        return (
            qs.model.objects.filter(candidates__isnull=False)
            .annotate(**annotation)
            .aggregate(**{f'score_{yr}_max': Max(f'score_{yr}') for yr in years})
        )
    maximums = {}
    roots = qs.model.objects.filter(
        uid__in=[f'{schema.upper()}-ROOT' for schema in settings.SUBJECT_SCHEMAS]
    )
    for root in roots:
        maximums[root.tree_id] = (
            root.get_descendants()
            .annotate(**annotation)
            .aggregate(**{f'score_{yr}_max': Max(f'score_{yr}') for yr in years})
        )
    return maximums


def update_normalized_scores(qs: QuerySet, field: str, stats: Optional[Counter] = None) -> None:
    years = [*YEARS, 'all']
    maximums = get_maximums(qs, field)
    objs_to_update = []
    logger.info(f'Updating normalized scores for {field}')
    for obj in tqdm(qs.iterator(chunk_size=10_000), total=qs.count()):
        max_dict = maximums if field != 'subject_categories' else maximums.get(obj.tree_id)
        if not max_dict:
            continue
        scores_dict = {
            f'score_{yr}': (
                100 * (getattr(obj, f'score_{yr}') or 0) / max_dict[f'score_{yr}_max']
                if max_dict[f'score_{yr}_max']
                else None
            )
            for yr in years
        }
        if obj.normalized_score != scores_dict:
            obj.normalized_score = scores_dict
            objs_to_update.append(obj)
    qs.model.objects.bulk_update(objs_to_update, ['normalized_score'], batch_size=1000)
    if stats is not None:
        stats[f'{field}_normalized_score_updated'] = len(objs_to_update)


def update_scores_for_model(qs: QuerySet, field: str, stats: Optional[Counter] = None) -> None:
    objs_to_update = []
    logger.info(f'Updating static scores for {field}')
    for obj in tqdm(qs.iterator(chunk_size=10_000), total=qs.count()):
        scores_dict = {f'score_{yr}': getattr(obj, f'score_{yr}') for yr in YEARS}
        scores_dict['score_all'] = obj.score_all
        if obj.static_score != scores_dict:
            obj.static_score = scores_dict
            objs_to_update.append(obj)
    qs.model.objects.bulk_update(objs_to_update, ['static_score'], batch_size=1000)
    if stats is not None:
        stats[f'{field}_static_scores_updated'] = len(objs_to_update)
    update_normalized_scores(qs, field, stats=stats)


def update_static_scores(
    work_set: WorkSet, stats: Optional[Counter] = None, new_hits: List[WorkHit] = None
) -> None:
    agg_dict = make_annotations_dict()
    for model, field in MODELS_TO_UPDATE:
        qs = model.objects.filter(work_set=work_set)
        if new_hits:
            qs = qs.filter(works__workhit__in=new_hits)
        qs = qs.annotate(**agg_dict)
        update_scores_for_model(qs, field, stats=stats)


def update_growth_fields(work_set: WorkSet, chunk_size=10_000) -> Counter:
    stats = Counter()
    fields_to_update = ['score_past_yr', 'score_yr_b4', 'absolute_growth', 'relative_growth']
    models_list = [
        Work,
        Author,
        Publisher,
        Language,
        SubjectCategory,
        WorkCategory,
        OwnerInstitution,
    ]
    qs_list = [
        model.objects.filter(work_set=work_set).annotate_relative_growth() for model in models_list
    ]
    for qs in qs_list:
        logger.info(f'Updating {qs.model.__name__} objects...')
        with atomic():
            objs_to_update = []
            for obj in tqdm(qs.iterator(chunk_size=chunk_size), total=qs.count()):
                if (
                    obj.score_past_yr == obj.annotated_score_past_yr
                    and obj.score_yr_b4 == obj.annotated_score_yr_b4
                ):
                    continue
                for field in fields_to_update:
                    setattr(obj, field, getattr(obj, f'annotated_{field}'))
                objs_to_update.append(obj)
                if objs_to_update and len(objs_to_update) % chunk_size == 0:
                    qs.model.objects.bulk_update(objs_to_update, fields_to_update, batch_size=1000)
                    stats[f'{qs.model.__name__}_objects_updated'] += chunk_size
                    objs_to_update = []
            qs.model.objects.bulk_update(objs_to_update, fields_to_update, batch_size=1000)
            stats[f'{qs.model.__name__}_objects_updated'] += len(objs_to_update)
    return stats
