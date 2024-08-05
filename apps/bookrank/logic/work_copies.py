import itertools as it
import re
from collections import Counter
from datetime import date
from decimal import Decimal, InvalidOperation
from string import whitespace

from django.conf import settings

from ..models import Work, WorkCopy


def format_date(date_str: str) -> date:
    if not date_str:
        return None
    year = int(date_str[:4])
    month = int(date_str[4:6]) or 1
    day = int(date_str[6:]) or 1
    try:
        return date(year, month, day)
    except ValueError:
        print('Strange year', date_str, year, month, day)
        return None


def format_price(price_str: str):
    if not price_str:
        return None, None
    if '/' in price_str:
        price_str = price_str.split('/')[0]
    currency_li = re.findall(r'[a-zčA-ZČ]+', price_str)
    czk_variants = ['KČ', 'KČS', 'Kč']
    if not currency_li or currency_li[0] in czk_variants:
        currency = 'CZK'
    else:
        currency = currency_li[0].upper()
    price = re.findall(r'[\d\.,]+', price_str)
    if not price:
        return None, None
    price = price[0].replace(',', '.')
    price = price.strip(whitespace + '.')
    price = re.sub(r'\.{2,}', '.', price)  # replace more than one '.' for exactly one
    try:
        return Decimal(price), currency
    except InvalidOperation:
        print('Impossible to convert price', price_str, price)
        return None, None


def assign_fields(work_copy: WorkCopy, copy_dict: dict, to_create: bool):
    field_map = [field.split('__') for field in settings.WORKCOPIES_FIELDMAP]
    to_update = False
    for db_field, marc_field in field_map:
        if db_field == 'acquisition_date':
            acq_date = format_date(copy_dict.get(marc_field))
            if to_create or acq_date != work_copy.acquisition_date:
                work_copy.acquisition_date = acq_date
                to_update = not to_create
        if db_field == 'price':
            price, currency = format_price(copy_dict.get(marc_field))
            if to_create or work_copy.price != price or work_copy.currency != currency:
                work_copy.price = price
                work_copy.currency = currency
                to_update = not to_create
    return work_copy, to_update


def create_copies(work: Work, stats: Counter) -> None:
    data = work.extra_data.get('aleph', {}).get('copies', [])
    copies = []
    for copy_dict in data:
        work_copy, _ = assign_fields(WorkCopy(work=work), copy_dict, True)
        copies.append(work_copy)
    created = WorkCopy.objects.bulk_create(copies)
    stats['work_copies_created'] += len(created)


def update_copies(work: Work, stats: Counter) -> None:
    data = work.extra_data.get('aleph', {}).get('copies', [])
    old_copies = work.copies.order_by('created')
    field_map = [field.split('__') for field in settings.WORKCOPIES_FIELDMAP]
    fields_to_update = [field[0] for field in field_map]
    if 'price' in fields_to_update:
        fields_to_update.append('currency')
    for_update = []
    for_create = []
    pks_for_delete = []
    for copy_dict, copy_obj in it.zip_longest(data, old_copies):
        to_create = False
        if not copy_dict and copy_obj:
            pks_for_delete.append(copy_obj.pk)
            continue
        if not copy_obj:
            to_create = True
            copy_obj = WorkCopy(work=work)
        copy_obj, to_update = assign_fields(copy_obj, copy_dict, to_create)
        if to_create:
            for_create.append(copy_obj)
        if to_update:
            for_update.append(copy_obj)
    deleted_count, _ = work.copies.filter(pk__in=pks_for_delete).delete()
    stats['work_copies_deleted'] += deleted_count
    created = WorkCopy.objects.bulk_create(for_create)
    stats['work_copies_created'] += len(created)
    WorkCopy.objects.bulk_update(for_update, fields_to_update)
    stats['work_copies_updated'] += len(for_update)
