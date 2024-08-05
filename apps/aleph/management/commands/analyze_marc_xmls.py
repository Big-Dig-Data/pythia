import csv
import json
import logging
import re
import tarfile
import xml.etree.ElementTree as ET
from collections import Counter
from itertools import combinations, product
from pathlib import Path
from pprint import pprint

from django.core.management.base import BaseCommand
from tqdm import tqdm

from ...logic.data_import import fix_code

logger = logging.getLogger(__name__)


def aleph_marc_xml_to_dict(filename: str, is_content=False) -> dict:
    try:
        et = ET.fromstring(filename) if is_content else ET.parse(filename)
    except Exception as e:
        logger.error('Error parsing file "%s"', filename)
        raise e
    root = et.getroot()
    ret = {}
    for el in root:
        tag_name = el.tag
        if "}" in tag_name:  # remove namespace
            tag_name = tag_name.split("}")[1]
        if tag_name == 'controlfield' and el.attrib.get('tag') == '008':
            ret['lang'] = el.text[35:38].strip()
            ret['catalog_date'] = el.text[0:6]
        elif tag_name == 'datafield':
            tag_num = el.attrib.get('tag')
            if tag_num not in ret:
                ret[tag_num] = []
            subfields = {fix_code(sf.attrib.get('code', '')): sf.text for sf in el}
            ret[tag_num].append(subfields)
    return ret


class Command(BaseCommand):

    help = (
        'Reads data from Aleph AOI XML format and prints out a statistics of values for a '
        'specific field identified by `tag` and `letter`'
    )

    def add_arguments(self, parser):
        parser.add_argument('dirname', type=str)
        parser.add_argument(
            'tags',
            type=str,
            nargs='*',
            help='Name of MARC element in for of tag-subtag, like 650-a, or 250-7',
        )
        parser.add_argument('--sample', type=int, default=0, dest='sample')

    def handle(self, *args, **options):
        stats = Counter()
        values = Counter()
        input_dir = Path(options['dirname'])
        tags = [tag.split('-') for tag in options['tags']]
        sample = options['sample']

        def process_dict(records):
            all_values = []
            for field in tags:
                if len(field) == 1:
                    tag, letter = field[0], None
                else:
                    tag, letter = field
                index = None
                if letter:
                    m = re.match(r'(.+)\[(\d+)]', letter)
                    if m:
                        letter = m.group(1)
                        index = int(m.group(2))
                tag_values = []
                if tag in records:
                    if type(records[tag]) is list:
                        for rec in records[tag]:
                            if letter in rec:
                                raw_value = rec[letter]
                                if index is not None:
                                    raw_value = raw_value[index]
                                tag_values.append(raw_value)
                                stats['hit'] += 1
                            else:
                                stats['tag_no_letter'] += 1
                    else:
                        tag_values.append(records[tag])
                        stats['hit'] += 1
                else:
                    stats['no_tag'] += 1
                all_values.append(tag_values or [None])  # we need at least one value for product
            for comb in product(*all_values):
                values[tuple(comb)] += 1

        try:
            if input_dir.is_file():
                # assume tar file
                with tarfile.open(input_dir) as intar:
                    total = len(intar.getnames())
                    for i, tarinfo in enumerate(tqdm(intar, total=total)):
                        f = intar.extractfile(tarinfo)
                        if not f:
                            continue
                        data = aleph_marc_xml_to_dict(f)
                        process_dict(data)
                        if sample and i == sample:
                            logger.info('Reached sample size %d', sample)
                            break
            else:
                total = sum(1 for _x in input_dir.iterdir())
                total = sample if sample else total
                for i, file_path in enumerate(tqdm(input_dir.iterdir(), total=total)):
                    try:
                        data = aleph_marc_xml_to_dict(file_path)
                    except ET.ParseError as exc:
                        logger.error('Error in file %s: %s', file_path, exc)
                    process_dict(data)
                    if sample and i == sample:
                        logger.info('Reached sample size %d', sample)
                        break
        except KeyboardInterrupt:
            pass
        logger.info('Stats: %s', stats)
        print("Stats:", stats)
        pprint(values.most_common(20))
        name_base = '__'.join(options['tags'])
        filename = f'dump-{name_base}.csv'
        with open(filename, 'w') as outfile:
            writer = csv.writer(outfile)
            writer.writerow([*options['tags'], 'count'])
            for key, value in sorted(values.items(), key=lambda x: -x[1]):
                writer.writerow([*key, value])
        logger.info('Values were dumped into "%s"', filename)
