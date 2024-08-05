import logging
from collections import Counter
from tqdm import tqdm

from django.db.transaction import atomic
from django.core.management.base import BaseCommand

from ...models import SubjectCategory, WorkSet


logger = logging.getLogger(__name__)

DEFAULT_WORKSET = 'Aleph'
DEFAULT_FILE = 'data/konspekt_aut.txt'


class Command(BaseCommand):
    help = 'Creates tree of Konspekt subjects'

    def add_arguments(self, parser):
        parser.add_argument(
            'work_set',
            type=str,
            default=DEFAULT_WORKSET,
            nargs='?',
            help="Work set name, if not present, Aleph is assumed",
        )
        parser.add_argument(
            'source_file',
            type=str,
            default=DEFAULT_FILE,
            nargs='?',
            help="Source file path as a string",
        )

    @atomic
    def handle(self, *args, **options):
        work_set, _ = WorkSet.objects.get_or_create(name=options['work_set'])
        source_file = options['source_file']
        node_dicts = self.get_nodes(source_file)
        total_nodes = len(node_dicts)
        stats = Counter()
        stats['total'] = total_nodes
        with SubjectCategory.objects.disable_mptt_updates():
            root_node, _ = SubjectCategory.objects.get_or_create(
                work_set=work_set,
                uid='KONSPEKT-ROOT',
                defaults={'name': 'KONSPEKT', 'is_controlled_dictionary': True},
            )
            existing_cats = {cat.uid: cat for cat in root_node.get_descendants()}
            cats_for_update = []
            for node_dict in tqdm(node_dicts, total=total_nodes):
                uid, name = node_dict['uid'], node_dict['name']
                if cat := existing_cats.get(uid, None):
                    if name != cat.name:
                        cat.name = name
                        cats_for_update.append(cat)
                        stats['updated'] += 1
                    continue
                parent_uid = node_dict.get('parent')
                parent = existing_cats[parent_uid] if parent_uid else root_node
                new_cat = SubjectCategory.objects.create(
                    work_set=work_set,
                    uid=uid,
                    name=name,
                    parent=parent,
                    is_controlled_dictionary=False,
                )
                existing_cats[uid] = new_cat
                stats['created'] += 1
            if cats_for_update:
                SubjectCategory.objects.bulk_update(cats_for_update, ['name'])
        logger.info('Rebuilding MPTT index')
        SubjectCategory.objects.rebuild()
        logger.info(stats)

    def get_nodes(self, source_file):
        node_dicts = []
        with open(source_file, 'r') as f:
            while True:
                line = f.readline()
                if not line:
                    break
                node_raw = line.strip().split('$$')[1:]
                node_dict = {x[0]: x[1:] for x in node_raw}
                node_dicts.append(self.format_node_dict(node_dict))
        return node_dicts

    def format_node_dict(self, node: dict) -> dict:
        uid = node.get('k', node.get('a'))
        node_dict = {'name': node.get('x')}
        parent = node.get('9')
        if parent:
            node_dict['parent'] = f'KONSPEKT-PARENT-{parent}'
            node_dict['uid'] = f'KONSPEKT-{uid}'
        else:
            node_dict['uid'] = f'KONSPEKT-PARENT-{uid}'
        return node_dict
