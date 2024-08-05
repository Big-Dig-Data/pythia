from typing import Union

from django.db.models.fields.json import KeyTextTransform, KeyTransform
from django.db.models import Manager, QuerySet, FloatField, F, Subquery, OuterRef, Max, Value
from django.db.models.functions import Coalesce, Cast


class CandidateQuerySet(QuerySet):
    def annotate_score_lowlevel(
        self, weights: dict, year: Union[int, str], score_type: str
    ) -> QuerySet:
        qs = self
        for k, v in weights.items():
            model = self.model._meta.get_field(k).related_model
            # here is some inspiration for this query -
            # https://docs.djangoproject.com/en/3.2/ref/models/expressions/#using-aggregates-within-a-subquery-expression
            # values('candidates') enforces group by candidate in the subquery, otherwise
            # a different grouping will be created which messes the query up
            score_subquery = (
                model.objects.filter(candidates=OuterRef('pk'))
                .order_by()
                .values('candidates')
                .annotate(
                    score=Cast(
                        v
                        * Coalesce(
                            Max(
                                Cast(
                                    KeyTextTransform(f'score_{year}', f'{score_type}_score'),
                                    FloatField(),
                                )
                            ),
                            0,
                        ),
                        output_field=FloatField(),
                    )
                )
                .values('score')[:1]
            )

            qs = qs.annotate(**{f'{k}_score': Subquery(score_subquery, output_field=FloatField())})

        return qs.annotate(
            score=F('authors_score')
            + F('languages_score')
            + F('subjects_score')
            + F('publisher_score')
        )

    def annotate_score(self, weights: dict, year: Union[int, str], score_type: str) -> QuerySet:
        qs = self
        for k, v in weights.items():
            qs = qs.annotate(
                **{
                    f'{k}_score': v
                    * (
                        Cast(
                            Coalesce(
                                KeyTextTransform(
                                    f'{k}_score',
                                    KeyTransform(f'score_{year}', f'{score_type}_scores'),
                                ),
                                Value('0'),
                            ),
                            FloatField(),
                        )
                    )
                }
            )
        return qs.annotate(
            score=F('authors_score')
            + F('languages_score')
            + F('subjects_score')
            + F('publisher_score')
        )


CandidateManager = Manager.from_queryset(CandidateQuerySet)
