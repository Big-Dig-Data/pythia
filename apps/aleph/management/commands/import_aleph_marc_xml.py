"""
Read OAI files from Aleph and import them into the database
"""

import logging
from collections import Counter
from pathlib import Path
from xml.etree.ElementTree import ParseError

from django.core.management.base import BaseCommand
from django.db.transaction import set_autocommit, commit
from tqdm import tqdm

from ...logic.data_import import import_aleph_marc_xml, filename_to_uid
from ...models import AlephEntry

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = 'Reads data from Aleph AOI XML format and imports it into the database'
    sync_states = ['no change', 'created', 'updated']

    def add_arguments(self, parser):
        parser.add_argument('dirname', type=str)
        parser.add_argument(
            '-a',
            '--all',
            action='store_true',
            dest='all',
            help='Process all files - regardless of timestamp',
        )
        parser.add_argument(
            '-d',
            '--delete-missing',
            action='store_true',
            dest='delete_missing',
            help='Delete records for which a file was not found',
        )
        parser.add_argument(
            '-x',
            '--disable-transactions',
            action='store_true',
            dest='disable_transactions',
            help='Do not use transaction management - warning leads to SLOW processing.',
        )

    def handle(self, *args, **options):
        stats = Counter()
        do_all = options.get('all', False)
        input_dir = Path(options['dirname'])
        use_transactions = not options.get('disable_transactions', False)
        if use_transactions:
            set_autocommit(False)
        total = sum(1 for _x in input_dir.iterdir())
        uid_to_mod_time = {
            x[0]: x[1].timestamp()
            for x in AlephEntry.objects.all().values_list('uid', 'last_updated')
        }
        seen_uids = set()
        try:
            for i, file_path in enumerate(tqdm(input_dir.iterdir(), total=total)):
                uid = filename_to_uid(str(file_path))
                seen_uids.add(uid)
                mtime = uid_to_mod_time.get(uid)
                if do_all or (not mtime or mtime < file_path.stat().st_mtime):
                    try:
                        entry, status = import_aleph_marc_xml(str(file_path))
                    except ParseError:
                        stats['xml_error'] += 1
                    else:
                        stats[self.sync_states[status]] += 1
                else:
                    stats['skipped'] += 1
                if i % 10000 == 0 and use_transactions:
                    commit()
            if use_transactions:
                commit()
        except KeyboardInterrupt:
            logger.info("Stats: %s", stats)
            raise
        logger.info("Stats: %s", stats)
        if use_transactions:
            set_autocommit(True)
        all_uids = set(AlephEntry.objects.all().values_list('uid', flat=True))
        missing_uids = all_uids - seen_uids
        logger.info('Found %d records without a file', len(missing_uids))
        if options['delete_missing']:
            deleted = AlephEntry.objects.filter(uid__in=missing_uids).delete()
            logger.info('Deleted %d records without a file. Details: %s', deleted[0], deleted[1])
        else:
            logger.info('Use -d to delete them')
