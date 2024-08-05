import logging
from time import monotonic

from django.core.management import CommandError
from django.core.management.base import BaseCommand

from importers.onix import ImportOnix21Reference
from source_data.logic.data_import import sync_data_with_source
from source_data.models import DataSource

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = 'Reads data from ONIX2.1 XML format and imports it into the database'

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)
        self.start = monotonic()

    def add_arguments(self, parser):
        parser.add_argument('source', type=str)
        parser.add_argument('filename', type=str, nargs='+')
        parser.add_argument('-c', '--create-source', dest='create_source', action='store_true')

    def handle(self, *args, **options):
        source_name = options['source']
        try:
            source = DataSource.objects.get(slug=source_name)
        except DataSource.DoesNotExist:
            if options.get('create_source', False):
                source = DataSource.objects.create(slug=source_name)
            else:
                sources = ','.join(DataSource.objects.all().values_list('slug', flat=True))
                raise CommandError(
                    f'No such source "{source_name}". Use -c to create it or '
                    f'use one of the existing sources: {sources}'
                )
        for fname in options['filename']:
            reader = ImportOnix21Reference(fname)
            stats = sync_data_with_source(reader, source, watcher=self.show_progress)
            self.stderr.write(f'\nStats: {stats}')

    def show_progress(self, count):
        if count and count % 10 == 0:
            seconds = monotonic() - self.start
            print(f'\r{count} records in {seconds:.1f} s  => {count/seconds:.1f} rps', end='')
