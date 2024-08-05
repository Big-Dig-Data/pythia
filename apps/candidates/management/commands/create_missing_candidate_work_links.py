import logging

from django.core.management.base import BaseCommand
from django.db.transaction import atomic

from ...models import CandidateWorkLink

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = (
        'Creates `CandidateWorkLinks` where `Work` and `Candidate` ISBNs match and the link '
        'is not already present'
    )

    @atomic
    def handle(self, *args, **options):
        count = CandidateWorkLink.create_missing_links()
        logger.info('New links created: %d', count)
