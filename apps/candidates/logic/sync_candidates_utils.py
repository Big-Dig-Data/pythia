import re
import json
from copy import deepcopy
from decimal import Decimal
from html import unescape
from typing import Callable, Optional, Type, Union

from django.db import models
from django.utils.html import strip_tags
import xmltodict

from bookrank.models import Author, Language, Publisher, WorkSet
from source_data.models import DataRecord
from ..models import Agent

DIRECT_VALS = {
    'title': [('Title', {}), ('TitleText', '')],
    'edition': [('EditionNumber', None)],
    'availability': [('SupplyDetail', {}), ('ProductAvailability', None)],
    'supplier': [('SupplyDetail', {}), ('SupplierName', '')],
    'price': [('SupplyDetail', {}), ('Price', {}), ('PriceAmount', Decimal(0))],
    'price_currency': [('SupplyDetail', {}), ('Price', {}), ('CurrencyCode', '')],
    'product_format': [('ProductForm', '')],
}
EXTRA_FIELDS = ('RecordReference', 'ProductIdentifier', 'Subject', 'MediaFile')


def extract_product_data(record: DataRecord) -> dict:
    raw_data = xmltodict.parse(record.raw_data.data.tobytes())
    product_data = json.loads(json.dumps(raw_data['ONIXMessage']['Product']))
    if isinstance(product_data, list):
        return product_data[0]
    return product_data


class NamedModelManager:
    def __init__(self, work_set: WorkSet, model: Type[models.Model]):
        self.work_set = work_set
        self.model = model
        self.name_to_obj = {
            rec['name']: rec['pk']
            for rec in self.model.objects.filter(work_set=self.work_set).values('name', 'pk')
        }

    def get_by_name(self, name: str):
        pk = self.name_to_obj.get(name)
        created = False
        if not pk:
            obj, created = self.model.objects.get_or_create(name=name, work_set=self.work_set)
            self.name_to_obj[name] = obj.pk
            pk = obj.pk
        return pk, created


class RecordToCandidateDict:
    def __init__(self, record: DataRecord, work_set: WorkSet) -> None:
        self.record = extract_product_data(record)
        self.work_set = work_set

    def map_fields(
        self,
        agent_map,
        publisher_manager: NamedModelManager,
        lang_manager: NamedModelManager,
        author_manager: NamedModelManager,
    ) -> dict:
        pub_name = re.sub(r' \(.+\)$', '', self.record['Publisher']['PublisherName'])
        pub_name = self.recursive_unescape(strip_tags(pub_name))
        publisher, pub_created = publisher_manager.get_by_name(pub_name)

        market_rep = self.record['MarketRepresentation']
        agent_key = (market_rep['AgentName'], market_rep['EmailAddress'])
        agent = agent_map.get(agent_key)
        agent_created = False
        if not agent:
            agent, agent_created = Agent.objects.get_or_create(
                name=agent_key[0], email=agent_key[1]
            )
            agent_map[agent_key] = agent  # store for other records

        return {
            'data': {
                **{k: self.extract_nested_vals(v) for k, v in DIRECT_VALS.items()},
                'publisher_id': publisher,
                'agent': agent,
                'abstract': self.get_abstract(),
                'extra_data': {k: self.record.get(k, {}) for k in EXTRA_FIELDS},
                'publication_year': self.get_pub_year(),
            },
            'publishers_created': pub_created,
            'agents_created': agent_created,
            'authors': self.extract_m2m_data(
                'Contributor', 'PersonName', author_manager, fmt_func=self.format_author_name
            ),
            'languages': self.extract_m2m_data('Language', 'LanguageCode', lang_manager),
        }

    def extract_nested_vals(self, keys: list):
        val = deepcopy(self.record)
        for el in keys:
            val = val.get(*el)
        val = self.recursive_unescape(strip_tags(val))
        return self.remove_latex(val)

    def extract_m2m_data(
        self,
        onix_outer: str,
        onix_inner: str,
        manager: NamedModelManager,
        fmt_func: Optional[Callable[[str], str]] = None,
    ) -> dict:
        obj_li = self.record.get(onix_outer)
        if not obj_li:
            obj_li = []
        elif isinstance(obj_li, dict):
            obj_li = [obj_li]
        names = [obj[onix_inner] for obj in obj_li]
        if fmt_func:
            names = [fmt_func(name) for name in names]
        model_objs = []
        num_created = 0
        for name in names:
            model_obj, created = manager.get_by_name(name=name)
            model_objs.append(model_obj)
            if created:
                num_created += 1
        return {'entries': model_objs, 'num_created': num_created}

    def format_author_name(self, author: str) -> str:
        author = self.recursive_unescape(strip_tags(author))
        li = author.split(' ')
        return f'{li[-1]}, {" ".join(li[:-1])}'

    def get_abstract(self) -> str:
        other_text = self.record.get('OtherText', {})
        if isinstance(other_text, list):
            other_text = other_text[0]
        other_text = other_text.get('Text') or ''
        other_text = self.recursive_unescape(strip_tags(other_text))
        return self.remove_latex(other_text)

    def get_pub_year(self):
        date_raw = self.record.get('PublicationDate', '')
        date_raw = self.recursive_unescape(strip_tags(date_raw))
        date_raw = self.remove_latex(date_raw)
        if len(date_raw) < 8:
            return None
        return date_raw[:4]

    def recursive_unescape(self, s: str) -> str:
        new_s = unescape(s)
        return new_s if new_s == s else self.recursive_unescape(new_s)

    def remove_latex(self, s: str) -> str:
        matches = re.findall(r"\{\\mathcal \w+\}", s)
        for m in matches:
            replace_str = m.replace('{\\mathcal ', '')
            replace_str = replace_str.replace('}', '')
            s = s.replace(m, replace_str)
        matches = re.findall(r"\$.+\$", s)
        for m in matches:
            s = s.replace(m, m.replace('$', ''))
        return s
