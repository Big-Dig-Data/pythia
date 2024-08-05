"""
Fetches PSH data from the API
"""

import logging
from collections import Counter
from pathlib import Path

import requests

from django.core.management.base import BaseCommand
from django.db.transaction import atomic

from ...logic.command_help import get_workset_by_name_or_command_error
from ...models import SubjectCategory


logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = 'Fetches PSH data from the API'
    URL_TEMP = 'https://psh.techlib.cz/api/concepts/{}'
    # CACHE_DIR = Path('_psh_cache')

    def __init__(self, stdout=None, stderr=None, no_color=False):
        super().__init__(stdout, stderr, no_color)
        self.db_uid_to_pk = {}
        self.session = None
        self.counter = Counter()
        self.workset = None

    def add_arguments(self, parser):
        parser.add_argument(
            '-t',
            type=str,
            dest='top',
            default="top",
            help="PSHID of concept where to start the search",
        )
        parser.add_argument('workset', type=str, help="Name or UUID of the WorkSet to use.")

    @atomic
    def handle(self, *args, **options):
        self.workset = get_workset_by_name_or_command_error(options['workset'], self)
        # if not self.CACHE_DIR.exists():
        #     raise ValueError("Cache dir: {} is missing".format(self.CACHE_DIR))
        db_root, _ = SubjectCategory.objects.get_or_create(
            uid='PSH-ROOT', name='PSH', parent=None, work_set=self.workset
        )
        self.session = requests.session()
        self.db_uid_to_pk = {
            rec['uid']: rec['pk']
            for rec in SubjectCategory.objects.filter(tree_id=db_root.tree_id).values('uid', 'pk')
        }
        logger.info("Found %d concepts in the DB", len(self.db_uid_to_pk))
        with SubjectCategory.objects.disable_mptt_updates():
            for top in options['top'].split(','):
                data = self.session.get(self.URL_TEMP.format(top)).json()
                if '@graph' not in data:
                    logger.warning("Error fetching data for %s", top)
                    self.counter['error'] += 1
                    continue
                # when going from top, a list of concepts is retrieved, otherwise only one record
                records = data['@graph'] if top == 'top' else [data['@graph']]
                for rec in records:
                    self.process_psh_record(rec)
        logger.info('Rebuilding MPTT index')
        SubjectCategory.objects.rebuild()
        self.stderr.write("Stats: {}".format(self.counter))

    def process_psh_record(self, record: dict) -> str:
        # if self.counter['created'] > 200:
        #     return ''
        uid = record['pshid']
        parent_id = record['broader'] or 'PSH-ROOT'
        if uid not in self.db_uid_to_pk:
            parent_pk = self.db_uid_to_pk.get(parent_id)
            if not parent_pk:
                logger.warning('Missing parent %s for %s', parent_id, uid)
                self.counter['missing parent'] += 1
                return ''
            name = record['prefLabel']['cs']
            sc = SubjectCategory.objects.create(
                parent_id=parent_pk, uid=uid, name=name, work_set=self.workset
            )
            self.db_uid_to_pk[uid] = sc.pk
            self.counter['created'] += 1
            logger.info("Created: %s", uid)
        else:
            self.counter['existing'] += 1
            logger.info("Skipped existing: %s", uid)
        for child_id in record['narrower']:
            if child_id not in self.db_uid_to_pk:
                data = self.session.get(self.URL_TEMP.format(child_id)).json()
                self.process_psh_record(data['@graph'])
            else:
                self.counter['existing'] += 1
                logger.info("Skipped existing: %s", child_id)
        return uid
