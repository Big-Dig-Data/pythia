import csv
import logging
from collections import Counter, defaultdict
from tqdm import tqdm

from django.db.transaction import atomic
from django.db.models import Q
from django.core.management.base import BaseCommand

from bookrank.models import SubjectCategory, WorkSet
from ...models import Candidate

logger = logging.getLogger(__name__)

DEFAULT_WORKSET = 'Aleph'
TRANS_CSV = 'data/bic_to_thema/bic_to_thema_t1.csv'


class Command(BaseCommand):
    help = 'Assigns Thema categories to Works'

    def add_arguments(self, parser):
        parser.add_argument(
            'work_set',
            type=str,
            default=DEFAULT_WORKSET,
            nargs='?',
            help="Work set name, if not present, Aleph is assumed",
        )
        parser.add_argument(
            '-a', '--all', action='store_true', dest='process_all', help="Process all candidates"
        )

    @atomic
    def handle(self, *args, **options):
        work_set, _ = WorkSet.objects.get_or_create(name=options['work_set'])
        candidates = (
            Candidate.objects.prefetch_related('subjects')
            .filter(
                Q(extra_data__contains={'Subject': [{'SubjectSchemeIdentifier': '12'}]})
                | Q(extra_data__contains={'Subject': {'SubjectSchemeIdentifier': '12'}})
            )
            .distinct()
        )
        process_all = options.get('process_all', False)
        if not process_all:
            candidates = candidates.filter(subjects__isnull=True)
        stats = Counter()
        total = candidates.count()
        stats['total'] = total
        translation_table = self.create_translation_table(TRANS_CSV)
        for candidate in tqdm(candidates.iterator(), total=total):
            subjects_list = candidate.extra_data.get('Subject', {})
            if isinstance(subjects_list, list):
                bic_codes = [
                    el['SubjectCode']
                    for el in subjects_list
                    if el['SubjectSchemeIdentifier'] == '12'
                ]
            else:
                bic_codes = (
                    [subjects_list['SubjectCode']]
                    if subjects_list.get('SubjectSchemeIdentifier') == '12'
                    else []
                )
            if not bic_codes:
                continue
            bic_codes = self.remove_ancestors(bic_codes)
            thema_codes = self.translate_codes(bic_codes, translation_table, stats)
            if not thema_codes:
                continue
            subjects = SubjectCategory.objects.filter(uid__in=thema_codes, work_set=work_set)
            if process_all:
                candidate_subjects = set(candidate.subjects.values_list('uid', flat=True))
                if candidate_subjects != thema_codes:
                    candidate.subjects.clear()
                    candidate.subjects.add(*subjects)
                    stats['updated'] += 1
            else:
                candidate.subjects.add(*subjects)
                stats['updated'] += 1

        logger.info(stats)

    def create_translation_table(self, filename: str) -> dict:
        with open(filename, 'r') as infile:
            reader = csv.DictReader(infile)
            out = defaultdict(set)
            for row in reader:
                for col in ['Thema Subj 1', 'Thema Subj 2', 'Thema Subj 3']:
                    if val := row.get(col, '').strip():
                        out[row['BIC Subject Code is exactly']].add(val)
        return out

    def translate_codes(self, bic_codes: list, trans: dict, stats: Counter) -> set:
        thema_codes = set()
        for bic in bic_codes:
            th_codes = trans[bic]
            if not th_codes:
                stats['not_found'] += 1
                continue
            thema_codes |= set(th_codes)
        return thema_codes

    def remove_ancestors(self, codes: list) -> list:
        result = []
        while codes:
            code = codes.pop()
            if not any(el.startswith(code) for el in codes + result):
                result.append(code)
        return result
