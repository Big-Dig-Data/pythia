"""
Read OAI files from Aleph and import them into the database
"""

import logging
from collections import Counter
from pathlib import Path
from xml import etree

from tqdm import tqdm
from elasticsearch.helpers import bulk
from elasticsearch import Elasticsearch

from django.core.management.base import BaseCommand

from ...logic.data_import import filename_to_uid, aleph_marc_xml_to_dict

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = 'Reads data from Aleph AOI MARC XML format and imports it into elasticsearch'
    index_name = 'marc'
    doc_type = '_doc'

    def add_arguments(self, parser):
        parser.add_argument('dirname', type=str)

    def handle(self, *args, **options):
        stats = Counter()
        input_dir = Path(options['dirname'])
        es = Elasticsearch()
        bulk(es, self.gen_data(input_dir))
        logger.info("Stats: %s", stats)

    def gen_data(self, input_dir):
        total = sum(1 for _x in input_dir.iterdir())
        for i, file_path in enumerate(tqdm(input_dir.iterdir(), total=total)):
            uid = filename_to_uid(str(file_path))
            try:
                data = aleph_marc_xml_to_dict(file_path)
            except etree.ElementTree.ParseError as exc:
                logger.error("Parser error in #%s: %s", uid, exc)
                continue
            rec = {'uid': uid, 'data': data}
            yield {"_index": self.index_name, "_type": self.doc_type, "_source": rec}
