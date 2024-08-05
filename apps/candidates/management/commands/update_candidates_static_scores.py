import logging
from collections import Counter

from django.core.management.base import BaseCommand
from django.db.transaction import atomic

from bookrank.models import WorkSet
from bookrank.logic.static_score import update_static_scores as update_topics_static_scores
from ...logic.static_scores import update_candidates_static_scores

logger = logging.getLogger(__name__)

DEFAULT_WORKSET = 'Aleph'


class Command(BaseCommand):

    help = 'Updates the `static_scores` precomputed field for all candidates'

    def add_arguments(self, parser):
        parser.add_argument(
            'work_set',
            type=str,
            default=DEFAULT_WORKSET,
            nargs='?',
            help=f"Work set name, if not present, {DEFAULT_WORKSET} is assumed",
        )

    def handle(self, *args, **options):
        work_set, _ = WorkSet.objects.get_or_create(name=options['work_set'])
        topics_stats = Counter()
        with atomic():
            update_topics_static_scores(work_set, topics_stats)
            logger.info(topics_stats)
        with atomic():
            stats = update_candidates_static_scores(callback=self.callback, score_type='static')
            logger.info('Overall stats for static scores: %s', stats)
        with atomic():
            stats = update_candidates_static_scores(callback=self.callback, score_type='normalized')
            logger.info('Overall stats for normalized scores: %s', stats)

    @classmethod
    def callback(cls, year, number, stats):
        logger.info('Year: %s; records: %d  (stats: %s)', year, number, stats)
