import logging
import sys

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count

from tabulate import tabulate

from core.logic.logging import query_counter
from ...models import WorkSet, WorkTopic

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = 'Prints statistics about a WorkSet specified by a name or UUID'

    def add_arguments(self, parser):
        parser.add_argument(
            'work_set', type=str, help="Name or UUID of the WorkSet to use.", nargs='?'
        )

    def print_worksets(self):
        worksets = [
            (ws.name, ws.uuid, ws.size, ws.mi_count)
            for ws in WorkSet.objects.all().annotate(
                size=Count('works', distinct=True), mi_count=Count('mis', distinct=True)
            )
        ]
        self.stdout.write(self.style.SUCCESS("Available work-sets:\n"))
        self.stdout.write(
            tabulate(
                worksets, headers=['name', 'uuid', 'work count', 'mi count'], tablefmt='presto'
            )
        )

    def handle(self, *args, **options):
        if options['work_set']:
            try:
                workset = WorkSet.objects.get(name=options['work_set'])
            except WorkSet.DoesNotExist:
                try:
                    workset = WorkSet.objects.get(uuid=options['work_set'])
                except (WorkSet.DoesNotExist, ValidationError):
                    self.print_worksets()
                    raise CommandError("invalid workset name or UUID given")
        else:
            self.print_worksets()
            self.stdout.write(self.style.WARNING("\nGive me work-set name of UUID for more info"))
            sys.exit()
        logger.info('Working with workset: %s, UUID: %s', workset, workset.uuid)
        # basic statistics
        with query_counter(logger):
            work_count = workset.works.count()
            topic_count = workset.topics.count()
            wt_links_count = WorkTopic.objects.filter(work__work_set=workset).count()
        table = [
            ("Works", work_count),
            ("Topics", topic_count, topic_count / work_count),
            ("Work-topic links", wt_links_count, wt_links_count / work_count),
        ]
        self.stdout.write('\n============\nBasic stats:\n============')
        self.stdout.write(tabulate(table, headers=['items', 'count', 'per work'], floatfmt=".2f"))
        # model instances
        mis = [
            (mi.name, mi.model.name, mi.uuid) for mi in workset.mis.all().select_related('model')
        ]
        self.stdout.write(
            '\n\n=========================\nBookrank model instances:\n' '========================='
        )
        self.stdout.write(tabulate(mis, headers=['name', 'model', 'uuid'], floatfmt='.2f'))
        # topic types
        topic_types = [
            (t['typ'], t['count'], 100 * t['count'] / topic_count, t['count'] / work_count)
            for t in workset.topics.all().values('typ').order_by('typ').annotate(count=Count('pk'))
        ]
        self.stdout.write('\n\n============\nTopic types:\n============')
        self.stdout.write(
            tabulate(topic_types, headers=['type', 'count', '% total', 'per work'], floatfmt='.2f')
        )
        # topic subtypes
        if False:
            topic_types = [
                (
                    t['typ'],
                    t['subtyp__name'],
                    t['count'],
                    100 * t['count'] / topic_count,
                    t['count'] / work_count,
                )
                for t in workset.topics.all()
                .values('typ', 'subtyp__name')
                .order_by('typ', 'subtyp__name')
                .annotate(count=Count('pk'))
            ]
            self.stdout.write('\n\n===============\nTopic subtypes:\n===============')
            self.stdout.write(
                tabulate(
                    topic_types,
                    headers=['type', 'subtype', 'count', '% total', 'per work'],
                    floatfmt='.2f',
                )
            )
