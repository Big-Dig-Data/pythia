"""
Loads hits from a CSV file
"""

import logging

from django.core.management import CommandError
from django.core.management.base import BaseCommand
from django.db import transaction

from bookrank.logic.command_help import get_workset_by_name_or_command_error
from ...logic.workhit_data import load_workhits_from_csv
from ...models import HitType

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = 'Loads hit data from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            'work_set', type=str, help="Name of the work set for which these hits were recorded"
        )
        parser.add_argument('hit_type', type=str, help="Name of the hit type to use for the data")
        parser.add_argument('csv_file', type=str, nargs="+")
        parser.add_argument(
            '-c',
            '--count-col',
            type=str,
            dest='count_col',
            default="count",
            help="Name of the column in which count (hit size) is stored.",
        )
        parser.add_argument(
            '-i',
            '--id-col',
            type=str,
            dest='id_col',
            default="id",
            help="Name of the column in which hit target ID is stored.",
        )
        parser.add_argument(
            '-d',
            '--date-col',
            type=str,
            dest='date_col',
            default="date",
            help="Name of the column in which hit date is stored.",
        )
        parser.add_argument(
            '-s',
            '--separator',
            type=str,
            dest='separator',
            default=",",
            help="Field separator for CSV.",
        )
        parser.add_argument(
            '-r',
            '--replace',
            action='store_true',
            dest='replace',
            help="If hits clash with DB, replace the existing records.",
        )
        parser.add_argument(
            '-a',
            '--add-hit-type',
            action='store_true',
            dest='add_hit_type',
            help="If hit_type does not exist, create it, otherwise throw error.",
        )
        parser.add_argument(
            '-f',
            '--field-names',
            type=str,
            dest='field_names',
            default="",
            help="If CSV does not have a header, you can specify the comma "
            "separated list of names here.",
        )

    def handle(self, *args, **options):
        fieldnames = None
        if options['field_names']:
            fieldnames = [x.strip() for x in options['field_names'].split(",")]
        separator = options['separator']
        if separator == 'TAB':
            separator = '\t'
        workset = get_workset_by_name_or_command_error(options['work_set'], self)
        with transaction.atomic():
            # get or create hit_type
            hit_type_name = options['hit_type']
            try:
                hit_type = HitType.objects.get(slug=hit_type_name)
            except HitType.DoesNotExist:
                if options['add_hit_type']:
                    hit_type = HitType.objects.create(slug=hit_type_name)
                    logger.info("Created new HitType: %s", hit_type.slug)
                else:
                    self.stderr.write(
                        self.style.WARNING(
                            '* available hit types are: {}'.format(
                                ', '.join(ht.slug for ht in HitType.objects.all())
                            )
                        )
                    )
                    self.stderr.write(
                        self.style.WARNING('* or use -a to create the supplied HitType')
                    )
                    raise CommandError(f'Unknown HitType "{hit_type_name}"')
            else:
                logger.debug("Using existing HitType: %s, pk: %d", hit_type.slug, hit_type.pk)
            # load the data
            for fname in options['csv_file']:
                logger.info('Reading file: %s', fname)
                stats = load_workhits_from_csv(
                    fname,
                    workset,
                    hit_type,
                    id_col=options['id_col'],
                    date_col=options['date_col'],
                    count_col=options['count_col'],
                    fieldnames=fieldnames,
                    separator=separator,
                    replace_existing=options['replace'],
                )
                self.stderr.write(self.style.NOTICE(f'Stats: {stats}'))
