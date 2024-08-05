import csv
import logging
from collections import Counter

from django.db.models import QuerySet, Count
from django.db.transaction import atomic
from django.core.management.base import BaseCommand
from django.contrib.postgres.aggregates import ArrayAgg

from tqdm import tqdm

from candidates.models import Candidate
from ...models import WorkSet, Author, Publisher, Work
from ...logic.cleanup import normalize_name

logger = logging.getLogger(__name__)

DEFAULT_WORKSET = 'Aleph'


class Command(BaseCommand):
    help = 'Cleans up and merges authors and publishers'

    def add_arguments(self, parser):
        parser.add_argument(
            'work_set',
            type=str,
            default=DEFAULT_WORKSET,
            nargs='?',
            help="Work set name, if not present, Aleph is assumed",
        )
        parser.add_argument(
            '-d',
            '--debug',
            action='store_true',
            dest='debug',
            help="Only creates csv files with proposed changes, doesn't change db",
        )

    @atomic
    def handle(self, *args, **options):
        work_set, _ = WorkSet.objects.get_or_create(name=options['work_set'])
        authors = Author.objects.filter(work_set=work_set)
        publishers = Publisher.objects.filter(work_set=work_set)
        stats = Counter()
        stats['authors_before_merge'] = authors.count()
        stats['publishers_before_merge'] = publishers.count()
        authors_to_change = self.clean_up(authors, stats, 'authors')
        pubs_to_change = self.clean_up(publishers, stats, 'publishers')

        if options.get('debug', False):
            self.write_csv(authors_to_change, pubs_to_change)
            logger.info('CSV files with proposed changes created in root of project')
            logger.info('Filenames: "authors_to_change.csv" and "publishers_to_change.csv"')
            return None

        Author.objects.bulk_update([el[-1] for el in authors_to_change], ['name'])
        Publisher.objects.bulk_update([el[-1] for el in pubs_to_change], ['name'])
        self.merge(authors, 'authors', stats)
        self.merge(publishers, 'publishers', stats)
        logger.info(stats)

    def clean_up(self, qs: QuerySet, stats: Counter, qs_name: str) -> list:
        changed = []
        logger.info(f'Normalizing {qs_name} names...')
        for obj in tqdm(qs.iterator(), total=stats[f'{qs_name}_before_merge']):
            name = normalize_name(obj.name)
            if name != obj.name:
                old_name = obj.name
                obj.name = name
                changed.append([str(obj.pk), old_name, name, obj])
        return changed

    def merge(self, qs: QuerySet, qs_name: str, stats: Counter) -> None:
        logger.info(f'Merging {qs_name}...')
        names_qs = (
            qs.values('name').annotate(count=Count('id'), ids=ArrayAgg('id')).filter(count__gt=1)
        )
        ids_to_delete = []
        candidates_to_update = []
        for obj in names_qs:
            obj_that_stays = obj['ids'][0]
            throw_away = obj['ids'][1:]
            works = Work.objects.filter(**{f'{qs_name}__pk__in': throw_away})
            for work in works:
                relation = getattr(work, qs_name)
                relation.add(obj_that_stays)
            candidates_to_update += self.add_topic_obj_to_candidates(
                obj_that_stays, throw_away, qs_name
            )
            ids_to_delete += throw_away
        if candidates_to_update:
            Candidate.objects.bulk_update(candidates_to_update, ['publisher'])
        stats[f'{qs_name}_deleted'], _ = qs.model.objects.filter(pk__in=ids_to_delete).delete()

    def add_topic_obj_to_candidates(self, obj_that_stays, throw_away_ids, topic_name):
        for_update = []
        if topic_name == 'publishers':
            candidates = Candidate.objects.filter(publisher__pk__in=throw_away_ids)
            publisher = Publisher.objects.get(pk=obj_that_stays)
            for candidate in candidates:
                candidate.publisher = publisher
                for_update.append(candidate)
        elif topic_name == 'authors':
            candidates = Candidate.objects.filter(authors__pk__in=throw_away_ids)
            for candidate in candidates:
                candidate.authors.add(obj_that_stays)
        else:
            raise ValueError(f'Unsupported topic name: {topic_name}')
        return for_update

    def write_csv(self, authors, pubs):
        for li, li_name in ((authors, 'authors'), (pubs, 'publishers')):
            with open(f'{li_name}_to_change.csv', 'w') as f:
                writer = csv.writer(f)
                writer.writerow(['PK', 'Old name', 'New name'])
                writer.writerows([el[:-1] for el in li])
