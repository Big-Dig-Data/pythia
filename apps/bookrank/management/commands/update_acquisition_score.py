import logging
from collections import Counter
from tqdm import tqdm

from django.db import transaction
from django.core.management.base import BaseCommand
from django.db.models import F

from ...models import Work, WorkSet


logger = logging.getLogger(__name__)

DEFAULT_WORKSET = 'Aleph'
BATCH_SIZE = 1000


class Command(BaseCommand):
    help = 'Updates Work acquisition score'

    def add_arguments(self, parser):
        parser.add_argument(
            'work_set',
            type=str,
            default=DEFAULT_WORKSET,
            nargs='?',
            help=f"Work set name, if not present, {DEFAULT_WORKSET} is assumed",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        stats = Counter()
        work_set, _ = WorkSet.objects.get_or_create(name=options['work_set'])
        # acquisition_score - db column; score - annotated value
        works = (
            Work.objects.filter(work_set=work_set)
            .annotate_score(score_type='acquisition_score', low_level=True)
            .exclude(score=F('acquisition_score'), acquisition_date=F('annotated_acquisition_date'))
        )
        to_update = []
        logger.info('Updating acquisition scores...')
        total = works.count()
        for i, work in tqdm(enumerate(works.iterator(chunk_size=BATCH_SIZE)), total=total):
            work.acquisition_score = work.score
            work.acquisition_date = work.annotated_acquisition_date
            to_update.append(work)
            if i and i % BATCH_SIZE == 0:
                Work.objects.bulk_update(to_update, ['acquisition_score', 'acquisition_date'])
                stats['updated'] += len(to_update)
                to_update = []
        Work.objects.bulk_update(to_update, ['acquisition_score', 'acquisition_date'])
        stats['updated'] += len(to_update)
        logger.info(stats)
