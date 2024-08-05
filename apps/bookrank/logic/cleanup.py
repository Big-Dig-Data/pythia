import re
from string import whitespace
from collections import Counter

from django.db.models import Count

from ..models import WorkSet, Publisher, Author, Language, WorkCategory, OwnerInstitution


def clean_unused_topics_by_type(workset: WorkSet, topic_model):
    """
    Given a topic_model subclass of ExplicitTopic, it deletes instances without any associated
    works
    :param workset:
    :param topic_model:
    :return:
    """
    deleted, info = (
        topic_model.objects.annotate(work_count=Count('works'))
        .filter(work_set=workset, work_count=0)
        .delete()
    )
    return deleted


def clean_all_unused_topics(workset: WorkSet):
    """
    Cleans up all types of explicit topic outside SubjectCategory, because it may come from a
    controlled dictionary
    :param workset:
    :return:
    """
    stats = Counter()
    for topic_model in (Publisher, Author, Language, WorkCategory, OwnerInstitution):
        stats[topic_model.__name__] += clean_unused_topics_by_type(workset, topic_model)
    return stats


def remove_unpaired_quotes(s: str) -> str:
    s = re.sub(r'(?<=\w)"(?=\w)', '', s)
    m_iter = re.finditer(r'"\w[^"]*\w"|"\w"', s)
    spans = [x.span() for x in m_iter]
    if not spans:
        return s.replace('"', '')
    new_s = ''
    first_span_flag = True
    for i, (first, second) in enumerate(spans):
        start = 0 if first_span_flag else spans[i - 1][1]
        first_span_flag = False
        end = first
        new_s += s[start:end].replace('"', '') + s[first:second]
    new_s += s[spans[-1][1] : len(s)].replace('"', '')
    return new_s


def normalize_name(name: str) -> str:
    name = name.replace('=', '-')
    name = re.sub(r" \|\w .*", "", name)
    name = re.sub(r"[!@#\^\*_\<>]", "", name)
    # removes / if followed or preceded by non-word char
    name = re.sub(r"((?<!\w)\/|\/(?!\w))", "", name)
    # removes ; and : only if in middle of the word
    name = re.sub(r'(?<=\w)[;:](?=\w)', '', name)
    name = remove_unpaired_quotes(name)
    strip_str = whitespace + ",;:|"
    if not name.startswith('-'):
        strip_str += '-'
    name = name.strip(strip_str)
    return ' '.join(name.split())
