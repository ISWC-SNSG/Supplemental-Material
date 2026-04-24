from __future__ import annotations

import re
from datetime import date

CN_DATE = re.compile(r'(20\d{2}|19\d{2})年(?:(\d{1,2})月)?(?:(\d{1,2})日)?')


def parse_cn_date(text: str):
    match = CN_DATE.search(text or '')
    if not match:
        return None
    year = int(match.group(1))
    month = int(match.group(2) or 1)
    day = int(match.group(3) or 1)
    try:
        return date(year, month, day)
    except Exception:
        return None
