import logging

from django.core.management.base import BaseCommand

from ...logic.static_score import update_growth_fields
from ...models import WorkSet

logger = logging.getLogger(__name__)
DEFAULT_WORKSET = 'Aleph'


class Command(BaseCommand):
    help = 'Updates growth fields on Works and ExplicitTopics'

    def add_arguments(self, parser):
        parser.add_argument(
            'work_set',
            type=str,
            default=DEFAULT_WORKSET,
            nargs='?',
            help="Work set name, if not present, Aleph is assumed",
        )

    def handle(self, *args, **options):
        work_set, _ = WorkSet.objects.get_or_create(name=options['work_set'])
        update_growth_fields(work_set)
