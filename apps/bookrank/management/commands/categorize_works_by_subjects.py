import logging

from django.core.management.base import BaseCommand
from django.conf import settings

from core.logic.updates import update_last_date, get_last_date
from ...models import WorkSet
from ...logic.topics import KonspektWorkCategorization, ThemaWorkCategorization


logger = logging.getLogger(__name__)

DEFAULT_WORKSET = 'Aleph'

SCHEMAS = {'thema': ThemaWorkCategorization, 'konspekt': KonspektWorkCategorization}


class Command(BaseCommand):
    help = 'Assigns subject categories other than PSH to Works'

    def add_arguments(self, parser):
        parser.add_argument(
            'work_set',
            type=str,
            default=DEFAULT_WORKSET,
            nargs='?',
            help="Work set name, if not present, Aleph is assumed",
        )
        parser.add_argument(
            '-a',
            '--all',
            dest='ignore_last_update',
            action='store_true',
            help="Ignore last_update detection and process all works.",
        )

    def handle(self, *args, **options):
        work_set, _ = WorkSet.objects.get_or_create(name=options['work_set'])
        for schema in settings.SUBJECT_SCHEMAS:
            if schema == 'psh':
                continue
            last_update = (
                get_last_date(schema, logger) if not options['ignore_last_update'] else None
            )
            SCHEMAS[schema](work_set, newer_than=last_update).categorize_works()
            update_last_date(schema)
