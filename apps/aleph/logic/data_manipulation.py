import re
from typing import Optional

from isbnlib import is_isbn10, is_isbn13, to_isbn13, canonical


def extract_data_of_type(aleph_entry, typ: str):
    res = []
    for line in aleph_entry.raw_data:
        if line['type'] == typ:
            res.append(line['value'])
    return res


def get_title_from_marc(aleph_entry):
    out = ''
    aleph_data = aleph_entry.raw_data
    if 'title' in aleph_data:
        title_rec = aleph_data['title']
        a = None
        b = None
        for part in title_rec:
            if 'a' in part:
                a = part['a'].strip()
            if 'b' in part:
                b = part['b'].strip()
        if a and not b:
            out = a.rstrip(":/ ")
        elif a and b:
            out = a + " " + b.rstrip(":/ ")
        elif b:
            out = b.rstrip(":/ ")
    return out


def check_isbn(s: str) -> Optional[str]:
    '''
    checks if str is valid isbn and returns:
     - isbn13 in canonical form (digits only)
     - None if str doesn't contain valid isbn
    '''
    if not s or not isinstance(s, str):
        return None
    match = re.match(r'[\d\- X]{10,}', s)
    if not match:
        return None
    s = match[0]
    if is_isbn13(s):
        return canonical(s)
    if is_isbn10(s):
        return to_isbn13(s)
    return None


def extract_isbn(data: dict) -> list:
    '''
    data - dict based on AlephEntry.raw_data
    returns list of formated isbn13 strings or empty list if no isbn is in dict
    '''
    return [isbn for obj in data.get('isbn', []) if (isbn := check_isbn(obj.get('a', '')))]
