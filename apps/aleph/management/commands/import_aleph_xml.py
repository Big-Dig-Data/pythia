"""
Read OAI files from Aleph and import them into the database
"""

import logging
from collections import Counter
from pathlib import Path

from tqdm import tqdm

from django.core.management.base import BaseCommand
from django.db.transaction import atomic, set_autocommit, commit

from ...logic.data_import import import_aleph_xml, filename_to_uid
from ...models import AlephEntry

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = 'Reads data from Aleph AOI XML format and imports it into the database'

    def add_arguments(self, parser):
        parser.add_argument('dirname', type=str)

    def handle(self, *args, **options):
        stats = Counter()
        input_dir = Path(options['dirname'])
        set_autocommit(False)
        total = sum(1 for _x in input_dir.iterdir())
        uid_to_mod_time = {
            x[0]: x[1].timestamp()
            for x in AlephEntry.objects.all().values_list('uid', 'last_updated')
        }
        for i, file_path in enumerate(tqdm(input_dir.iterdir(), total=total)):
            uid = filename_to_uid(str(file_path))
            mtime = uid_to_mod_time.get(uid)
            if not mtime or mtime < file_path.stat().st_mtime:
                entry, created = import_aleph_xml(str(file_path))
                stats['created' if created else 'updated'] += 1
            else:
                stats['skipped'] += 1
            if i % 1000 == 0:
                commit()
        commit()
        logger.info("Stats: %s", stats)
