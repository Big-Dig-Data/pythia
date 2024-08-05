import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


def extract_publication_years_from_marc(marc_dict: dict) -> (Optional[int], Optional[int]):
    """
    Extracts (start, end) years from a MARC 21 record given in dict format. In most cases the
    start and end years will be the same as there is only one year, but it may be
    * num1, num2 - for series published over several years
    * num1, None - for series where publication still takes place
    * None, None - if not publication data is found
    :return:
    """
    records = marc_dict.get('pub', [])
    if records:
        year_rec = records[0].get('c')
        if year_rec:
            parts = year_rec.split('-')
            if len(parts) == 1:
                start = cleanup_marc_year(parts[0])
                return start, start
            elif len(parts) == 2:
                start = cleanup_marc_year(parts[0])
                if parts[1].strip():
                    return start, cleanup_marc_year(parts[1])
                else:
                    return start, None
    return None, None


def cleanup_marc_year(text: str) -> Optional[int]:
    """
    Takes text defining year as used in a MARC record 260c and returns an integer, if the value
    can be converted to one, or None if it can't be.
    """
    text = text.strip().lstrip('c, [/').rstrip('.[]?,/')
    try:
        num = int(text)
        if num > 3000 or num < 0:
            logger.error('Strange year number "%d"', num)
            return None
        return num
    except ValueError as exc:
        m = re.match(r'^(\d{4})\D*', text)
        if m:
            # we try to use the value from here
            return cleanup_marc_year(m.group(1))
        logger.error('Value "%s" could not be converted to year - exception: %s', text, exc)
        return None
