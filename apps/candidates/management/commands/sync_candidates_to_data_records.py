import logging
from collections import Counter

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q, F
from tqdm import tqdm

from source_data.models import DataRecord
from bookrank.models import Author, Language, WorkSet, Publisher
from ...models import Candidate, Agent
from ...logic.sync_candidates_utils import RecordToCandidateDict, NamedModelManager

logger = logging.getLogger(__name__)

DEFAULT_WORKSET = 'Aleph'
STATS_KEYS = ('publishers_created', 'agents_created')
M2M_FIELDS = ('authors', 'languages')


class Command(BaseCommand):

    help = (
        'Reads data from source_data.DataRecord and imports it into the candidates.Candidate table'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            'work_set',
            type=str,
            default=DEFAULT_WORKSET,
            nargs='?',
            help="Work set name, if not present, Aleph is assumed",
        )
        parser.add_argument(
            '-a',
            '--all',
            dest='ignore_last_updated',
            action='store_true',
            help="Ignore last_updated detection and process all data records.",
        )
        parser.add_argument(
            '-x',
            '--disable-transactions',
            dest='disable_transactions',
            action='store_true',
            help="Do not manage transactions inside code - WARNING leads to very slow progress!",
        )

    def handle(self, *args, **options):
        work_set, _ = WorkSet.objects.get_or_create(name=options['work_set'])
        stats = Counter()
        # the following construct with order_by and then distinct creates a (PostgreSQL specific?)
        # DISTINCT ON query which selects the distinct object based on the ordering applied
        # so in our case, it always gets us the newest object for a unique isbn13

        # prefetch related objects
        agent_map = {(agent.name, agent.email): agent for agent in Agent.objects.all()}
        publisher_manager = NamedModelManager(work_set, Publisher)
        lang_manager = NamedModelManager(work_set, Language)
        author_manager = NamedModelManager(work_set, Author)

        # prepare the query
        # we cannot do the distinct operation together with the filters because the query
        # would not be correct - for duplicated isbn when we process the newest record, it would
        # be filtered out and the second newest would come through. So we need to limit the
        # selection to the newest only before we apply other filters.
        data_records_to_consider = (
            DataRecord.objects.exclude(isbn13='')
            .order_by('isbn13', '-timestamp')
            .distinct('isbn13')
        )
        data_records = DataRecord.objects.select_related('raw_data').filter(
            id__in=data_records_to_consider
        )
        if not options['ignore_last_updated']:
            data_records = data_records.filter(
                Q(candidate__isnull=True) | Q(last_updated__gt=F('candidate__last_updated'))
            )
        total = data_records.count()
        stats['total'] = total

        # process all records
        #
        # Note:
        # we use manual transaction management to speed things up (about 2-3x) and that does not
        # work well with data_records.iterator. The problem is that the cursor used for each
        # batch by the iterator becomes invalid at the end of the iteration and the iterator
        # crashed with an error.
        #
        # To get around this, we use a different method which goes over the matching data records
        # by batches and then re-queries after each batch. In real life, it has the same speed
        # and other advantages as using iterator without its peculiarities.
        use_transactions = not options.get('disable_transactions', False)
        if use_transactions:
            transaction.set_autocommit(False)
        with tqdm(total=total) as progress:
            go_on = True
            start, end = 0, 1000
            while go_on:
                go_on = False
                for i, record in enumerate(data_records[start:end]):
                    data_dict = RecordToCandidateDict(record, work_set).map_fields(
                        agent_map, publisher_manager, lang_manager, author_manager
                    )
                    candidate, created = Candidate.objects.update_or_create(
                        isbn=record.isbn13, defaults={'data_record': record, **data_dict['data']}
                    )
                    if candidate.data_record != record:
                        # the data_record to use for this candidate may have changed
                        candidate.data_record = record
                        candidate.save()
                    self.update_m2m_fields(data_dict, candidate)
                    self.update_stats(stats, created, data_dict)
                    if i and i % 100 == 0 and use_transactions:
                        transaction.commit()
                    progress.update()
                    go_on = True
                # when ignoring last update, processed records do not automatically fall out
                # of the query, so we have to skip them "manually"
                if options['ignore_last_updated']:
                    start += 1000
                    end += 1000
                if use_transactions:
                    transaction.commit()
        if use_transactions:
            transaction.set_autocommit(True)
        logger.info(stats)

    def update_m2m_fields(self, full_data: dict, candidate: Candidate) -> None:
        for field_name in M2M_FIELDS:
            field = getattr(candidate, field_name)
            data = full_data[field_name]
            field.set(data['entries'])

    def update_stats(self, stats: Counter, candidate_created: bool, data: dict) -> None:
        if candidate_created:
            stats['candidates_created'] += 1
        else:
            stats['candidates_updated'] += 1
        for key in STATS_KEYS:
            stats[key] += int(data[key])
        for key in M2M_FIELDS:
            stats[f'{key}_created'] = data[key]['num_created']
