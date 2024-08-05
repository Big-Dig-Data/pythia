import logging
import operator
from collections import Counter
from csv import DictReader
from functools import reduce
from time import time

from anytree import NodeMixin
from anytree.exporter import DictExporter
from django.conf import settings
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Sum, QuerySet, Q, IntegerField, Count
from django.db.models.functions import Coalesce, Cast
from django.db.transaction import atomic
from tqdm import tqdm

from bookrank.models import SubjectCategory
from core.logic.query import prefix_query_filter

logger = logging.getLogger(__name__)


def extract_fk_explicit_topics_from_works(
    work_set: 'WorkSet',
    topic_extractor,
    topic_cls,
    attr_name,
    id_attr='name',
    newer_than=None,
    controlled_dictionary=False,
) -> Counter:
    stats = Counter()
    t = time()
    topic_filter = {}
    topics = {
        getattr(topic, id_attr): topic.pk
        for topic in topic_cls.objects.filter(work_set=work_set, **topic_filter)
    }
    logging.info("Have topics: %f", time() - t)
    work_qs = work_set.works.all()
    if newer_than:
        work_qs = work_qs.filter(last_updated__gt=newer_than)
    for i, work in enumerate(work_qs.iterator()):  # type: (int, 'Work')
        topic_names_subtypes_and_weights = topic_extractor(work)
        if len(topic_names_subtypes_and_weights) > 1:
            logger.error(
                'More than one value for foreign-key based explicit topic "%s", ' 'work: "%s"',
                topic_cls.__name__,
                work.uid,
            )
        if topic_names_subtypes_and_weights and topic_names_subtypes_and_weights[0][0] is not None:
            # if name is None, we deal with it the same way as if there was not name
            topic_name, _subtype_name, _ext_weight = topic_names_subtypes_and_weights[0]
            topic_db_id = topics.get(topic_name)
            # create the topic if it is not present
            if not topic_db_id:
                if controlled_dictionary:
                    stats['error'] += 1
                    logger.error(
                        f'Unknown value "{topic_name}" for controlled dictionary {topic_cls}'
                    )
                else:
                    topic = topic_cls.objects.create(name=topic_name, work_set=work_set)
                    topics[topic_name] = topic.pk
                    topic_db_id = topic.pk
                    stats['created'] += 1
            if getattr(work, attr_name + '_id') == topic_db_id:
                stats['skipped'] += 1
            else:
                setattr(work, attr_name + '_id', topic_db_id)
                work.save()
                stats['connected'] += 1
        else:
            # there was no value, check if we should clean it up
            if getattr(work, attr_name + '_id') is not None:
                setattr(work, attr_name + '_id', None)
                work.save()
                stats['disconnected'] += 1
        if i and i % 1000 == 0:
            logging.info("Extracted topics from %d works in %.2f seconds: %s", i, time() - t, stats)
    return stats


def extract_m2m_explicit_topics_from_works(
    work_set: 'WorkSet',
    topic_extractor,
    topic_cls,
    connector_cls,
    topic_filter=None,
    topic_extra_attrs=None,
    id_attr='name',
    newer_than=None,
    controlled_dictionary=False,
) -> Counter:
    stats = Counter()
    t = time()
    if topic_filter is None:
        topic_filter = {}
    if topic_extra_attrs is None:
        topic_extra_attrs = {}
    topics = {
        getattr(topic, id_attr): topic.pk
        for topic in topic_cls.objects.filter(work_set=work_set, **topic_filter)
    }
    logging.info("Have %d topics: %f s", len(topics), time() - t)
    connector_instances = []
    work_qs = work_set.works.all()
    if newer_than:
        work_qs = work_qs.filter(last_updated__gt=newer_than)
    connector_filter = prefix_query_filter(topic_filter, 'topic__')
    for i, work in enumerate(work_qs.iterator()):  # type: (int, 'Work')
        # logging.info("Extracted authors from %d works (%f)", i, time()-t)
        topic_names_subtypes_and_weights = topic_extractor(work)
        db_topic_ids = {
            wt.topic_id for wt in connector_cls.objects.filter(work=work, **connector_filter)
        }
        seen_topic_ids = set()
        for topic_name, _subtype_name, _ext_weight in topic_names_subtypes_and_weights:
            extra_attrs = {}
            if type(topic_name) is dict:
                _topic_name = topic_name.pop(id_attr)
                extra_attrs = topic_name
                topic_name = _topic_name
            topic_db_id = topics.get(topic_name)
            if topic_db_id:
                if topic_db_id in db_topic_ids:
                    stats['skipped'] += 1
                else:
                    connector_instances.append(connector_cls(work=work, topic_id=topic_db_id))
                    db_topic_ids.add(topic_db_id)
                    stats['connected'] += 1
                seen_topic_ids.add(topic_db_id)
            else:
                if controlled_dictionary:
                    stats['error'] += 1
                    logger.error(
                        f'Unknown value "{topic_name}" for controlled dictionary {topic_cls}'
                    )
                else:
                    # put the static extra attrs to the dynamic
                    extra_attrs.update(topic_extra_attrs)
                    topic = topic_cls.objects.create(
                        work_set=work_set, **{id_attr: topic_name}, **extra_attrs
                    )
                    topics[topic_name] = topic.pk
                    connector_instances.append(connector_cls(work=work, topic_id=topic.pk))
                    stats['created'] += 1
        # delete obsolete
        to_delete = db_topic_ids - seen_topic_ids
        if to_delete:
            stats['disconnected'] += 1
            connector_cls.objects.filter(work=work, topic_id__in=to_delete).delete()
        if i and i % 1000 == 0:
            logging.info("Extracted topics from %d works in %.2f seconds: %s", i, time() - t, stats)
    connector_cls.objects.bulk_create(connector_instances)
    return stats


marc_auth_type_to_weight = {'aut': 1.0, 'dis': 1.0, 'com': 0.8, 'edt': 0.9, '-': 1.0}


def marc_author_topics(work: 'Work') -> [(str, str, float)]:
    """
    Extracts author names from Work aleph data in MARC format
    :param work:
    :return:
    """
    aleph_data = work.extra_data.get('aleph', {})
    authors = aleph_data.get('author', []) + aleph_data.get('contrib', [])
    author_names = []
    for rec in authors:
        cont_type = rec.get('4', '-')  # contributor type
        if 'a' in rec and rec['a'] and cont_type in marc_auth_type_to_weight:
            author_names.append(
                (rec['a'].strip().rstrip(', '), None, marc_auth_type_to_weight[cont_type])
            )
    return author_names


def marc_subject_topics(work: 'Work') -> [(str, str, float)]:
    """
    Extracts subjects from Work aleph data in MARC format
    :param work:
    :return:
    """
    aleph_data = work.extra_data.get('aleph', {})
    subjects = []
    for subkey in ('udc', 'cat'):
        records = aleph_data.get(subkey, [])
        subjects += [
            (rec['a'].strip(), rec.get('2', None), 1.0)
            for rec in records
            if 'a' in rec and rec['a'].strip() and rec.get('2') != 'psh'
        ]
    return subjects


def marc_publisher_topics(work: 'Work') -> [(str, str, float)]:
    """
    Extracts publishers from Work aleph data in MARC format
    :param work:
    :return:
    """
    aleph_data = work.extra_data.get('aleph', {})
    records = aleph_data.get('pub', [])
    publishers = [(rec['b'].strip().strip(','), None, 1.0) for rec in records if 'b' in rec]
    return publishers


def marc_lang_topics(work: 'Work') -> [(str, str, float)]:
    """
    Extracts language from Work aleph data in MARC format
    :param work:
    :return:
    """
    aleph_data = work.extra_data.get('aleph', {})
    lang = aleph_data.get('lang', '')
    return [(lang, None, 1.0)]


def marc_psh_topics_simple(work: 'Work') -> [(str, str, float)]:
    """
    Extracts psh concepts from Work aleph data in MARC format
    Returns only explicitly assigned concepts
    """
    aleph_data = work.extra_data.get('aleph', {})
    ret = []
    for record in aleph_data.get('cat', []):
        if '2' in record and record['2'] == 'psh':
            pshid = record.get('7', '').upper()
            if pshid:
                ret.append((pshid, None, 1.0))
    return ret


def marc_topics_by_type(work: 'Work', topic_type) -> [(str, str, float)]:
    """
    Extracts topics from Aleph based on topic_type matching the corresponding MARC subfield
    """
    aleph_data = work.extra_data.get('aleph', {})
    ret = []
    for record in aleph_data.get('cat', []):
        if '2' in record and record['2'] == topic_type:
            topic = record.get('a')
            uid = record.get('7')
            if topic and uid:
                ret.append(({'name': topic, 'uid': uid}, None, 1.0))
    return ret


def marc_owner_institution_topics(work: 'Work') -> [(str, str, float)]:
    """
    Extracts owner organization from Work aleph data in MARC format - uses field 910a
    """
    aleph_data = work.extra_data.get('aleph', {})
    # try 910
    records = aleph_data.get('lib_info', [])
    if records:
        return [(records[0].get('a'), None, 1.0)]
    # try 040
    # records = aleph_data.get('record_source', [])
    # if records:
    #     return [(records[0].get('a'), None, 1.0)]
    return []


FIRST_LETTER_TO_CATEGORY = {
    'A': 'Monografie',
    'B': 'Monografie',
    'D': 'Monografie',
    'E': 'Monografie',
    'P': 'Časopisy',
    'R': 'Časopisy',
    'T': 'Časopisy',
    'F': 'Skripta',
    'O': 'Tuby s mapami',
    'W': 'Grantové zprávy',
    'G': 'Disertace',
    'H': 'Disertace',
    'X': 'Firemní literatura',
    'K': 'Kvalifikační práce, výroční zprávy',
}


def marc_work_category(work: 'Work') -> [(str, str, float)]:
    """
    Extracts work_category from Work aleph data in MARC format - uses field 910b
    """
    aleph_data = work.extra_data.get('aleph', {})
    records = aleph_data.get('lib_info', [])
    for record in records:
        val = record.get('b')
        if val:
            letter = val[0].upper()
            cat_name = FIRST_LETTER_TO_CATEGORY.get(letter, settings.DEFAULT_WORK_CATEGORY_NAME)
            return [(cat_name, None, 1.0)]
    return [(settings.DEFAULT_WORK_CATEGORY_NAME, None, 1.0)]


class SubjectNode(NodeMixin):
    def __init__(self, id, name, uid, score=None, parent=None, children=None):
        self.id = id
        self.name = name
        self.uid = uid
        self.score = score
        self.parent = parent
        if children:
            self.children = children


def build_subject_tree(root: SubjectCategory, score_type: str, cand_cnt_filters: dict) -> list:
    score_type_to_extra_fields = {
        'score': ['score'],
        'candidates_count': ['score'],
        'growth': ['score_past_yr', 'score_yr_b4', 'absolute_growth', 'relative_growth'],
    }
    root_node = SubjectNode(root.pk, root.name, root.uid)
    qs: QuerySet = root.get_descendants().exclude(uid__regex=r'^\d')
    base_fields = ['pk', 'name', 'uid', 'parent_id']
    extra_fields = score_type_to_extra_fields[score_type]
    if score_type == 'candidates_count':
        extra_filters = Q(candidates__isnull=False, **cand_cnt_filters)
        qs = qs.annotate(score=ArrayAgg('candidates__pk', filter=extra_filters))
    elif score_type == 'score':
        qs = qs.annotate(score=Coalesce(Cast('static_score__score_all', IntegerField()), 0))
        qs = qs.annotate(work_count=Coalesce(Count('works'), 0))
        base_fields.append('work_count')
    qs = qs.order_by('level', 'name').values(*[x for x in base_fields + extra_fields])
    pk_to_node = {root.pk: root_node}
    for rec in qs.iterator(chunk_size=10_000):
        pk = rec['pk']
        node = SubjectNode(pk, rec['name'], rec['uid'])
        pk_to_node[pk] = node
        node.parent = pk_to_node[rec['parent_id']]
        if 'work_count' in rec:
            node.work_count = rec['work_count']
        for field in extra_fields:
            setattr(node, field, rec[field])
    for rec in qs.reverse().iterator(chunk_size=10_000):
        node = pk_to_node[rec['pk']]
        for field in extra_fields:
            if field == 'relative_growth':
                node.acc_relative_growth = (
                    (node.acc_absolute_growth / node.acc_score_yr_b4)
                    if node.acc_score_yr_b4
                    else None
                )
                continue
            if score_type == 'candidates_count':
                init_val = rec[field] or []
            else:
                init_val = rec[field]
            setattr(node, f'acc_{field}', init_val)
            if node.children:
                setattr(
                    node,
                    f'acc_{field}',
                    sum((getattr(c, f'acc_{field}') for c in node.children), init_val),
                )
        if score_type == 'score':
            if node.children:
                node.acc_work_count = sum(
                    (c.acc_work_count for c in node.children), node.work_count
                )
            else:
                node.acc_work_count = node.work_count

    if score_type == 'candidates_count':
        for rec in qs:
            pk = rec['pk']
            pk_to_node[pk].acc_score = len(set(pk_to_node[pk].acc_score))
            del pk_to_node[pk].score
    exporter = DictExporter()
    return exporter.export(root_node)['children']


@atomic
class ThemaWorkCategorization:
    def __init__(self, work_set, newer_than=None):
        self.work_set = work_set
        self.newer_than = newer_than

    def categorize_works(self):
        works = self.work_set.works.filter(extra_data__aleph__lcc__isnull=False)
        if self.newer_than:
            works = works.filter(last_updated__gt=self.newer_than)
        total = works.count()
        stats = Counter()
        stats['total'] = total
        self.make_trans_dict()
        logger.info('Categorizing works by Thema...')
        for work in tqdm(works.iterator(), total=total):
            lcc_codes = [x for el in work.extra_data['aleph']['lcc'] if (x := el.get('a'))]
            thema_codes = self.lcc_to_thema(lcc_codes)
            if not thema_codes:
                continue
            subjects = SubjectCategory.objects.filter(work_set=self.work_set, uid__in=thema_codes)
            work.subject_categories.add(*subjects)
            stats['updated'] += 1
        logger.info(stats)

    def lcc_to_thema(self, lcc_list: list) -> set:
        thema_list = set()
        for lcc in lcc_list:
            thema_list |= set(self.trans_map.get(lcc, []))
        return thema_list

    def make_trans_dict(self):
        TRANS_FILE = 'data/_prevodLCC-Thema-proNTK.csv'
        with open(TRANS_FILE, 'r') as f:
            reader = DictReader(f)
            self.trans_map = {row['LCC'].replace(' ', ''): self.get_trans(row) for row in reader}

    def get_trans(self, row: dict) -> list:
        thema = row.get('Thema-znak')
        if not thema:
            thema = row.get('THEMA do záznamu (znak)')
        return thema.split('+')


@atomic
class KonspektWorkCategorization:
    def __init__(self, work_set, newer_than=None):
        self.work_set = work_set
        self.newer_than = newer_than

    def categorize_works(self):
        works = self.work_set.works.filter(
            extra_data__aleph__konspekt__isnull=False, work_set=self.work_set
        )
        if self.newer_than:
            works = works.filter(last_updated__gt=self.newer_than)
        total = works.count()
        updated = 0
        logger.info('Categorizing works by Konspekt...')
        for work in tqdm(works.iterator(chunk_size=10_000), total=total):
            subject_dicts = [el for el in work.extra_data['aleph']['konspekt']]
            subject_dicts = [x for x in subject_dicts if x.get('2') == 'Konspekt']
            subject_uids = [x for el in subject_dicts if (x := self.get_subject_uid(el))]
            if not subject_uids:
                continue
            subjects = SubjectCategory.objects.filter(work_set=self.work_set, uid__in=subject_uids)
            work.subject_categories.add(*subjects)
            updated += 1
        logger.info(f'updated: {updated}')

    def get_subject_uid(self, subject_dict):
        if uid := subject_dict.get('k'):
            return f'KONSPEKT-PARENT-{uid}'
        if uid := subject_dict.get('a'):
            return f'KONSPEKT-{uid}'
        return None
