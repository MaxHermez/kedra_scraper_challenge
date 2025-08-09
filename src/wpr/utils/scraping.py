from datetime import date
from dateutil.relativedelta import relativedelta

def month_ranges(start: date, end: date):
    """
    Yield (range_start, range_end_inclusive) month-slices until `end`.
    Example: (2024-01-01, 2024-02-01-1day), (2024-02-01, 2024-03-01-1day) …
    """
    cur = start.replace(day=1)
    while cur <= end:
        nxt = cur + relativedelta(months=1)
        yield cur, min(end, nxt - relativedelta(days=1))
        cur = nxt
