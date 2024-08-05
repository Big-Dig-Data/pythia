"""
Loads hits from a CSV file
"""

import logging
from time import time

from django.core.management.base import BaseCommand

from bookrank.logic.command_help import get_workset_by_name_or_command_error
from ...models import WorkHit

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = (
        'Takes hits from one year and copies the same data to one or more years. The purpose '
        'is to create artificial data for testing of larger datasets.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            'work_set', type=str, help="Name of the work set for which these hits were recorded"
        )
        parser.add_argument('from_year', type=int)
        parser.add_argument('to_year', type=int, nargs='+')

    def handle(self, *args, **options):
        workset = get_workset_by_name_or_command_error(options['work_set'], self)
        source = WorkHit.objects.filter(work__work_set=workset, date__year=options['from_year'])
        logger.info(
            'Found %d workhits for year %d and workset %s',
            source.count(),
            options['from_year'],
            workset,
        )
        for year in options['to_year']:
            start = time()
            logger.info('Copying to year %d', year)
            to_write = []
            for wh in source.iterator():
                new_date = wh.date.replace(year=year)
                to_write.append(
                    WorkHit(work_id=wh.work_id, value=wh.value, typ_id=wh.typ_id, date=new_date)
                )
            WorkHit.objects.bulk_create(to_write)
            logger.info('Copied %d work hits in %.2f s', len(to_write), time() - start)
