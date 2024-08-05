from collections import Counter
from typing import Iterator, Callable, Optional

from django.db.transaction import atomic

from importers.import_base import ImporterRecord

from ..models import DataSource, DataRecord, RawDataRecord


@atomic
def sync_data_with_source(
    reader: Iterator[ImporterRecord],
    source: DataSource,
    watcher: Optional[Callable[[int], None]] = None,
) -> Counter:
    stats = Counter()
    existing_ssids = set(source.datarecord_set.all().values_list('ssid', flat=True).distinct())
    i = 0
    for record in reader:
        defaults = {
            'isbn13': record.isbn or '',
            'title': record.title or '',
            'doi': record.doi or '',
            'other_ids': record.identifiers or {},
            'extracted_data': {},
        }

        record_obj, created = DataRecord.objects.update_or_create(
            ssid=record.ssid, timestamp=record.timestamp, source=source, defaults=defaults
        )
        if created:
            if record.ssid in existing_ssids:
                stats['new version created'] += 1
            else:
                stats['new ssid created'] += 1
        else:
            stats['existing record updated'] += 1
            record_obj.raw_data.delete()

        RawDataRecord.objects.create(
            record=record_obj, data=record.raw_data, fmt=record.raw_data_format.value
        )
        if watcher:
            watcher(i)
        i += 1
    return stats
