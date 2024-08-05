import json
import logging
from collections import Counter
from pathlib import Path

from django.core.management.base import BaseCommand

from core.logic.data_sources.google_books import GoogleBooksAPI
from ...models import AlephEntry

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = 'Downloads data from Google books for all relevant Aleph entries'

    def add_arguments(self, parser):
        parser.add_argument('-k', '--api-key', type=str, dest='api_key', default='')
        parser.add_argument('dirname', type=str)

    def handle(self, *args, **options):
        stats = Counter()
        outdir = Path(options['dirname'])
        api = GoogleBooksAPI(api_key=options['api_key'])
        for ae in AlephEntry.objects.filter(raw_data__isbn__isnull=False):
            isbn_data = ae.raw_data['isbn']
            stats['total'] += 1
            for subrec in isbn_data:
                if 'a' in subrec and subrec['a'].strip():
                    isbn = subrec['a']
                    break
            else:
                stats['no isbn'] += 1
                continue
            # here we continue with isbn surely filled
            cache_file = outdir / isbn
            if cache_file.exists():
                stats['in cache'] += 1
            else:
                logger.debug("Fetching: %s", isbn)
                data = api.get_info_by_isbn(isbn)
                with open(cache_file, 'w') as outfile:
                    json.dump(data, outfile, ensure_ascii=False, indent=2)
                if 'totalItems' not in data:
                    logger.warning("Something strange: %s", data)
                    if 'error' in data:
                        # we shut down on error
                        logger.error("There was an error, we shut down")
                        break
                else:
                    stats[data['totalItems']] += 1
                    stats['fetched'] += 1

        logger.info("Stats: %s", stats)
