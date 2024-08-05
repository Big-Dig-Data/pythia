import logging

from django.db.transaction import atomic
from django.core.management.base import BaseCommand

from core.logic.updates import update_last_date
from ...models import WorkSet
from ...logic.topics import KonspektWorkCategorization


logger = logging.getLogger(__name__)

DEFAULT_WORKSET = 'Aleph'


class Command(BaseCommand):
    help = 'Assigns Konspekt categories to Works'

    def add_arguments(self, parser):
        parser.add_argument(
            'work_set',
            type=str,
            default=DEFAULT_WORKSET,
            nargs='?',
            help="Work set name, if not present, Aleph is assumed",
        )

    @atomic
    def handle(self, *args, **options):
        work_set, _ = WorkSet.objects.get_or_create(name=options['work_set'])
        KonspektWorkCategorization(work_set).categorize_works()
        update_last_date('konspekt')
