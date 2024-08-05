"""
Fetches PSH data from the API
"""

import logging
from collections import Counter
from pathlib import Path

import requests

from django.core.management.base import BaseCommand
from django.db.transaction import atomic

from ...models import PSHConcept


logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = 'Fetches PSH data from the API'
    URL_TEMP = 'https://psh.techlib.cz/api/concepts/{}'
    # CACHE_DIR = Path('_psh_cache')

    def __init__(self, stdout=None, stderr=None, no_color=False):
        super().__init__(stdout, stderr, no_color)
        self.db_pshids = set()
        self.session = None
        self.counter = Counter()

    def add_arguments(self, parser):
        parser.add_argument(
            '-t',
            type=str,
            dest='top',
            default="top",
            help="PSHID of concept where to start the search",
        )

    @atomic
    def handle(self, *args, **options):
        # if not self.CACHE_DIR.exists():
        #     raise ValueError("Cache dir: {} is missing".format(self.CACHE_DIR))
        self.session = requests.session()
        self.db_pshids = {rec['pshid'] for rec in PSHConcept.objects.all().values('pshid')}
        logger.info("Found %d concepts in the DB", len(self.db_pshids))
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
        self.stderr.write("Stats: {}".format(self.counter))

    def process_psh_record(self, record: dict) -> str:
        # if self.counter['created'] > 200:
        #     return ''
        pshid = record['pshid']
        parent_id = record['broader'] or None
        if pshid not in self.db_pshids:
            if parent_id not in self.db_pshids:
                logger.warning('Missing parent %s for %s', parent_id, pshid)
                self.counter['missing parent'] += 1
                return ''
            name_cs = record['prefLabel']['cs']
            name_en = record['prefLabel']['en']
            PSHConcept.objects.create(
                parent_id=parent_id, pshid=pshid, name_cs=name_cs, name_en=name_en
            )
            self.db_pshids.add(pshid)
            self.counter['created'] += 1
            logger.info("Created: %s", pshid)
        else:
            self.counter['existing'] += 1
            logger.info("Skipped existing: %s", pshid)
        for child_id in record['narrower']:
            if child_id not in self.db_pshids:
                data = self.session.get(self.URL_TEMP.format(child_id)).json()
                self.process_psh_record(data['@graph'])
            else:
                self.counter['existing'] += 1
                logger.info("Skipped existing: %s", child_id)
        return pshid
