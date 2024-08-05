import json
import logging
from collections import Counter
from tqdm import tqdm

from django.db.transaction import atomic
from django.core.management.base import BaseCommand

from ...models import SubjectCategory, WorkSet


logger = logging.getLogger(__name__)

DEFAULT_WORKSET = 'Aleph'
DEFAULT_FILE = 'data/Thema_v1.4.2_en.json'


class Command(BaseCommand):
    help = 'Creates tree of Thema subjects'

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
        with open(source_file, 'r') as f:
            codes = json.load(f)['CodeList']['ThemaCodes']['Code']
        codes.sort(key=lambda el: len(el['CodeValue']))
        total_codes = len(codes)
        stats = Counter()
        stats['total'] = total_codes
        with SubjectCategory.objects.disable_mptt_updates():
            thema_root, _ = SubjectCategory.objects.get_or_create(
                work_set=work_set,
                uid='THEMA-ROOT',
                defaults={'name': 'THEMA', 'is_controlled_dictionary': True},
            )
            existing_cats = {cat.uid: cat for cat in thema_root.get_descendants()}
            cats_for_update = []
            for code in tqdm(codes, total=total_codes):
                uid, name = code['CodeValue'], code['CodeDescription']
                if cat := existing_cats.get(uid, None):
                    if name != cat.name:
                        cat.name = name
                        cats_for_update.append(cat)
                        stats['updated'] += 1
                    continue
                parent = self.get_parent(uid, work_set, thema_root)
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
        logger.info(stats)
        SubjectCategory.objects.rebuild()

    def get_parent(
        self, uid: str, work_set: WorkSet, thema_root: SubjectCategory
    ) -> SubjectCategory:
        if len(uid) > 1:
            if '-' in uid:
                parent_uid = uid.split('-')[0]
            else:
                parent_uid = uid[:-1]
            return SubjectCategory.objects.get(work_set=work_set, uid=parent_uid)
        return thema_root
