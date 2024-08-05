import csv
import datetime
import logging
from collections import Counter

from django.db.transaction import atomic

from bookrank.models import WorkSet
from bookrank.logic.static_score import update_static_scores
from core.logic.files import open_file
from ..models import HitType, WorkHit

logger = logging.getLogger(__name__)


@atomic
def load_workhits_from_csv(
    filename: str,
    workset: WorkSet,
    hit_type: HitType,
    separator=',',
    id_col='id',
    date_col='date',
    count_col='count',
    fieldnames=None,
    replace_existing=False,
) -> Counter:
    """

    :param filename:
    :param workset: only consider works from this workset when linking hits to works
    :param hit_type: type of hit that this file contains
    :param separator: CSV separator
    :param id_col: name of id column
    :param date_col: name of date column
    :param count_col: name of column with count
    :param fieldnames: provides fieldnames to CSV reader - usefull for files without headers
    :param replace_existing: if True, clashing WorkHits will be removed from the database
                             otherwise they will be not overwritten and new data forgotten
    :return:
    """
    new_hits = extract_workhits_from_csv(
        filename,
        workset,
        hit_type,
        separator=separator,
        fieldnames=fieldnames,
        id_col=id_col,
        date_col=date_col,
        count_col=count_col,
    )
    return sync_workhits_with_db(hit_type, new_hits, replace_existing=replace_existing)


def sync_workhits_with_db(
    hit_type: HitType, new_hits: [WorkSet], replace_existing=False
) -> Counter:
    stats = Counter()
    if not new_hits:
        return stats
    # here we check the database for conflicts
    min_date = min(wh.date for wh in new_hits)
    max_date = max(wh.date for wh in new_hits)
    existing_hits = WorkHit.objects.filter(date__gte=min_date, date__lte=max_date, typ=hit_type)
    existing_recs = {
        (wh['work_id'], wh['date']): (wh['pk'], wh['value'])
        for wh in existing_hits.values('pk', 'work_id', 'date', 'value').iterator()
    }
    to_insert = []
    to_delete = []
    for wh in new_hits:
        key = (wh.work_id, wh.date)
        clashing = existing_recs.get(key)
        if clashing is not None:
            if clashing[1] != wh.value:
                if replace_existing:
                    logger.warning(
                        'Overwriting different value for "%s": %s vs %s', key, clashing[1], wh.value
                    )
                    stats['replace'] += 1
                    to_insert.append(wh)
                    to_delete.append(clashing[0])  # the ID of the clashing WorkHit
                else:
                    logger.warning(
                        'Not overwriting different value for "%s": %s vs %s',
                        key,
                        clashing[1],
                        wh.value,
                    )
                    stats['no replace'] += 1
            else:
                stats['skip existing'] += 1
        else:
            stats['new'] += 1
            to_insert.append(wh)
    if to_insert:
        logger.info('Inserting %d new work hits', len(to_insert))
        hit_objs = WorkHit.objects.bulk_create(to_insert)
        update_static_scores(hit_objs[0].work.work_set, stats, new_hits=hit_objs)
    if to_delete:
        logger.info('Removing %d replaced work hits', len(to_delete))
        WorkHit.objects.filter(pk__in=to_delete).delete()
    return stats


def extract_workhits_from_csv(
    filename: str,
    workset: WorkSet,
    hit_type: HitType,
    separator=',',
    id_col='id',
    date_col='date',
    count_col='count',
    fieldnames=None,
) -> [WorkHit]:
    """
    Create unsaved WorkHit objects from a CSV file
    :param filename:
    :param workset: only consider works from this workset when linking hits to works
    :param hit_type: type of hit that this file contains
    :param separator: CSV separator
    :param id_col: name of id column
    :param date_col: name of date column
    :param count_col: name of column with count
    :param fieldnames: provides fieldnames to CSV reader - usefull for files without headers
    :return:
    """
    work_uid_to_pk = {x[1]: x[0] for x in workset.works.all().values_list('pk', 'uid')}
    # we use accumulator to merge together hits for one work on the same date, so that we only
    # insert one record into the DB for work-date combinations
    accumulator = Counter()
    i = 0
    with open_file(filename, 'rt') as infile:
        reader = csv.DictReader(infile, fieldnames=fieldnames, delimiter=separator)
        for i, rec in enumerate(reader):
            # target
            work_uid = rec.get(id_col, '').strip()
            if not work_uid:
                logger.warning('Record does not contain target ID (%s): %s', id_col, rec)
                continue
            work_pk = work_uid_to_pk.get(work_uid)
            if not work_pk:
                logger.error('No work with ID "%s" in workset "%s"', work_uid, workset)
                continue
            # date
            date_val = rec.get(date_col)
            if date_val:
                if len(date_val) == 8 or len(date_val) == 12:
                    date_val = datetime.date(
                        int(date_val[:4]), int(date_val[4:6]), int(date_val[6:8])
                    )
            # count
            count = rec.get(count_col, 1)  # default is 1
            # create the hit
            accumulator[(work_pk, date_val)] += int(count)
            if i and i % 1000 == 0:
                logger.debug('Read %d records', i)
    if i:
        logger.debug(
            'Read %d records, reduced into %d hits (%.2f %%)',
            (i + 1),
            len(accumulator),
            100 * (len(accumulator) / (i + 1)),
        )
    # in the following loop, we just prepare the objects, but we do not insert them into the db
    new_hits = []
    for (work_pk, date_val), count in accumulator.items():
        new_hits.append(WorkHit(work_id=work_pk, date=date_val, value=count, typ=hit_type))
    return new_hits
