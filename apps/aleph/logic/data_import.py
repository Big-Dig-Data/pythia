import re
import xml.etree.ElementTree as ET
import logging

from django.conf import settings

from ..models import AlephEntry

FILENAME_MATCHER = re.compile(r'\d{9}')
logger = logging.getLogger(__name__)


def aleph_xml_to_json(filename: str) -> list:
    et = ET.parse(filename)
    root = et.getroot()
    ret = []
    for el in root:
        value = el.text
        tag_name = el.tag
        if "}" in tag_name:
            tag_name = tag_name.split("}")[1]
        ret.append({'type': tag_name, 'value': value})
    return ret


def import_aleph_xml(filename: str) -> (AlephEntry, bool):
    data = aleph_xml_to_json(filename)
    uid = filename_to_uid(filename)
    return AlephEntry.objects.update_or_create(defaults={'raw_data': data}, uid=uid)


def filename_to_uid(filename) -> str:
    return FILENAME_MATCHER.search(filename).group(0)


def import_aleph_marc_xml(filename: str) -> (AlephEntry, int):
    """
    The second return value is
    0 if not update was performed,
    1 if entry was created,
    2 if update was performed
    :param filename:
    :return:
    """
    # in previous version we used update_or_create, but very often the update is not necessary
    # as the data is the same and updating all records is very slow.
    # This is why we now rather test for existence and equality - it is worse in worst case,
    # but much better in common cases
    data = aleph_marc_xml_to_dict(filename)
    uid = filename_to_uid(filename)
    try:
        rec = AlephEntry.objects.get(uid=uid)
    except AlephEntry.DoesNotExist:
        return AlephEntry.objects.create(raw_data=data, uid=uid), 1
    if rec.raw_data != data:
        rec.raw_data = data
        rec.save()
        return rec, 2
    else:
        rec.save()  # save to update `last_updated`
        return rec, 0


MARC_TAGS_OF_INTEREST = {
    '020': 'isbn',
    '080': 'udc',
    '040': 'record_source',
    '050': 'lcc',
    '072': 'konspekt',
    '100': 'author',
    '245': 'title',
    '260': 'pub',
    '264': 'pub',
    '650': 'cat',
    '700': 'contrib',
    '710': 'contrib_corp',
    '910': 'lib_info',
    '990': 'lib_custom',
    '996': 'copies',
}


def aleph_marc_xml_to_dict(filename: str) -> dict:
    try:
        et = ET.parse(filename)
    except Exception as e:
        logger.error('Error parsing file "%s"', filename)
        raise e
    root = et.getroot()
    ret = {}
    for el in root:
        tag_name = el.tag
        if "}" in tag_name:  # remove namespace
            tag_name = tag_name.split("}")[1]
        if tag_name == 'controlfield' and el.attrib.get('tag') == '008':
            ret['lang'] = el.text[35:38].strip()
            ret['catalog_date'] = el.text[0:6]
        elif tag_name == 'datafield':
            tag_num = el.attrib.get('tag')
            if tag_num in MARC_TAGS_OF_INTEREST:
                json_field = MARC_TAGS_OF_INTEREST[tag_num]
                if json_field not in ret:
                    ret[json_field] = []
                subfields = {fix_code(sf.attrib.get('code', '')): sf.text for sf in el}
                ret[json_field].append(subfields)
            if tag_num in settings.EXTRA_ALEPH_FIELDS:
                ret['_extra'] = ret.get('_extra', {})
                if tag_num not in ret['_extra']:
                    ret['_extra'][tag_num] = []
                ret['_extra'][tag_num].append(
                    {fix_code(sf.attrib.get('code', '')): sf.text for sf in el}
                )
    return ret


def fix_code(code: str) -> str:
    code = code.strip()
    if not code:
        return '-'
    return code
