import logging
from collections import Counter

from django.core.management.base import BaseCommand
from django.db.transaction import atomic
from tqdm import tqdm

from ...models import Work
from aleph.logic.data_manipulation import extract_isbn

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Populates missing isbn on Works based on stored extra_data"

    @atomic
    def handle(self, *args, **options):
        qs = Work.objects.filter(extra_data__aleph__isbn__isnull=False, isbn__len=0)
        total = qs.count()
        stats = Counter()
        stats['total'] = total
        for work in tqdm(qs.iterator(chunk_size=10_000), total=total):
            isbn_list = extract_isbn(work.extra_data['aleph'])
            if isbn_list:
                work.isbn = isbn_list
                work.save()
                stats['updated'] += 1
        logger.info(f"Stats: {stats}")
