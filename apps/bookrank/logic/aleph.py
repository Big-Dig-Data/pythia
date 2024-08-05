import re
from datetime import date
from typing import Optional


def convert_date_string(text: str, fmt='yymmdd') -> Optional[date]:
    text = re.sub(r'\D', '', text)
    yy = int(text[:2])
    mm = int(text[2:4])
    dd = int(text[4:6])
    if fmt == 'yyddmm':
        mm, dd = dd, mm
    today = date.today()
    if yy > (today.year - 2000):
        yy += 1900
    else:
        yy += 2000
    return date(year=yy, month=mm, day=dd)
