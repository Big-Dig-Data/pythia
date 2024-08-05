"""
Sync all AlephEntries from the aleph app to Works in the 'Book' category
"""

import logging
from collections import Counter

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db.models import Exists, OuterRef
from django.db.transaction import atomic
from tqdm import tqdm

from aleph.logic.data_manipulation import get_title_from_marc, extract_isbn
from aleph.models import AlephEntry
from ...logic.marc import extract_publication_years_from_marc
from ...logic.aleph import convert_date_string
from ...logic.work_copies import create_copies, update_copies
from ...models import Work, WorkCategory, WorkSet, Language

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = 'Reads data from aleph.AlephEntry and imports it into the bookrank.Work table'

    def add_arguments(self, parser):
        parser.add_argument(
            'work_set',
            type=str,
            help="Work set name or UUID, if not present, " "it will be created",
        )
        parser.add_argument('-f', '--filter-file', type=str, dest='filter_file')
        parser.add_argument('-a', '--all', action='store_true', dest='all')
        parser.add_argument('-d', '--delete', action='store_true', dest='delete_extra')

    @classmethod
    def read_uids(cls, filename) -> set:
        from csv import DictReader

        uids = set()
        with open(filename, 'r') as infile:
            reader = DictReader(infile)
            for rec in reader:
                uids.add(rec.get('uid'))
        return uids

    @atomic
    def handle(self, *args, **options):
        # get or create workset
        try:
            workset = WorkSet.objects.get(name=options['work_set'])
        except WorkSet.DoesNotExist:
            try:
                workset = WorkSet.objects.get(uuid=options['work_set'])
            except (WorkSet.DoesNotExist, ValidationError):
                workset = WorkSet.objects.create(name=options['work_set'])
                logger.info("Created workset '%s', UUID: %s", workset.name, workset.uuid)
        logger.debug("Using workset '%s', UUID: %s", workset.name, workset.uuid)
        # let's import
        stats = Counter()
        basic_aleph_exclude = {
            'raw_data__lib_custom__0__a__in': settings.DISALLOWED_WORK_CATEGORIES
        }
        if options['filter_file']:
            uids = self.read_uids(options['filter_file'])
            logger.info("Read %d UIDs to use from %s", len(uids), options['filter_file'])
            aleph_entry_queryset = AlephEntry.objects.filter(uid__in=uids).exclude(
                **basic_aleph_exclude
            )
        elif options['all']:
            aleph_entry_queryset = AlephEntry.objects.exclude(**basic_aleph_exclude)
        else:
            work_filter = Work.objects.filter(
                uid=OuterRef('uid'), last_updated__gte=OuterRef('last_updated')
            )
            aleph_entry_queryset = (
                AlephEntry.objects.annotate(has_newer_work=Exists(work_filter))
                .exclude(has_newer_work=True)
                .exclude(**basic_aleph_exclude)
            )
        lang_code_to_topic_id = {
            topic['name']: topic['pk']
            for topic in Language.objects.filter(work_set=workset).values('pk', 'name')
        }
        seen_work_pks = set()
        total = aleph_entry_queryset.count()
        catalog_date_stats = Counter()
        copies_stats = Counter()
        ignored_to_delete = set()
        if total:
            for aleph_entry in tqdm(aleph_entry_queryset.iterator(), total=total):
                if settings.ALEPH_IGNORE_FUNCTION:
                    if settings.ALEPH_IGNORE_FUNCTION(aleph_entry):
                        logger.info('Skipping ignored entry: %s', aleph_entry.uid)
                        stats['skipped'] += 1
                        ignored_to_delete.add(aleph_entry.uid)
                        continue
                lang_code = aleph_entry.raw_data.get('lang')
                if lang_code is not None:
                    lang_id = lang_code_to_topic_id.get(lang_code)
                    if lang_id is None:
                        lang_topic = Language.objects.create(name=lang_code, work_set=workset)
                        lang_code_to_topic_id[lang_code] = lang_topic.pk
                        lang_id = lang_topic.pk
                else:
                    lang_id = None
                if catalog_date := aleph_entry.raw_data.get('catalog_date', '').strip():
                    if settings.CATALOG_DATE_FORMAT_FUNCTION:
                        fmt = settings.CATALOG_DATE_FORMAT_FUNCTION(catalog_date, aleph_entry)
                    else:
                        fmt = settings.CATALOG_DATE_FORMAT
                    try:
                        catalog_date = convert_date_string(catalog_date, fmt=fmt)
                    except (ValueError, IndexError) as exc:
                        catalog_date_stats['error'] += 1
                        logger.error(
                            'Error converting date "%s": %s (UID: %s)',
                            catalog_date,
                            exc,
                            aleph_entry.uid,
                        )
                        catalog_date = None
                    else:
                        catalog_date_stats['ok'] += 1
                else:
                    catalog_date_stats['empty'] += 1
                    catalog_date = None

                # publication data
                start_yop, end_yop = extract_publication_years_from_marc(aleph_entry.raw_data)
                # find a name
                name = get_title_from_marc(aleph_entry)
                isbn_list = extract_isbn(aleph_entry.raw_data)
                try:
                    work = Work.objects.get(work_set=workset, uid=aleph_entry.uid)
                except Work.DoesNotExist:
                    work = None
                if work:
                    if (
                        work.name == name
                        and work.lang_id == lang_id
                        and work.start_yop == start_yop
                        and work.end_yop == end_yop
                        and work.extra_data.get('aleph', {}) == aleph_entry.raw_data
                        and work.isbn == isbn_list
                        and work.catalog_date == catalog_date
                    ):
                        stats['skipped'] += 1
                        work.save()  # we save to update last_updated date
                    else:
                        work.name = name
                        work.extra_data['aleph'] = aleph_entry.raw_data
                        work.lang_id = lang_id
                        work.start_yop = start_yop
                        work.end_yop = end_yop
                        work.isbn = isbn_list
                        work.catalog_date = catalog_date
                        work.save()
                        stats['updated'] += 1
                    if options['all'] or work.extra_data.get('aleph', {}).get(
                        'copies'
                    ) != aleph_entry.raw_data.get('copies'):
                        update_copies(work, copies_stats)
                else:
                    work = Work.objects.create(
                        uid=aleph_entry.uid,
                        work_set=workset,
                        name=name,
                        lang_id=lang_id,
                        extra_data={'aleph': aleph_entry.raw_data},
                        start_yop=start_yop,
                        end_yop=end_yop,
                        isbn=isbn_list,
                        catalog_date=catalog_date,
                    )
                    create_copies(work, copies_stats)
                    stats['created'] += 1
                seen_work_pks.add(work.pk)
        else:
            # there was nothing to sync
            logger.info('Nothing to sync')
        # let's process entries to be deleted
        aleph_entry_filter = AlephEntry.objects.filter(uid=OuterRef('uid')).exclude(
            **basic_aleph_exclude
        )
        work_qs = Work.objects.annotate(has_entry=Exists(aleph_entry_filter)).filter(
            has_entry=False
        )
        if options['delete_extra']:
            stats['deleted'] = work_qs.delete()
            stats['deleted'] = Work.objects.filter(uid__in=ignored_to_delete).delete()
        else:
            stats['to delete - not deleted'] = work_qs.count()
            stats['to delete - not deleted'] += Work.objects.filter(
                uid__in=ignored_to_delete
            ).count()
        logger.info("Stats: %s", stats)
        logger.info("Catalog date stats: %s", catalog_date_stats)
        logger.info("Work copies stats: %s", copies_stats)
