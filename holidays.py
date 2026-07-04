"""
Queensland public holidays, computed (no internet or package needed).
Covers the state-wide holidays — local show days are not included.
"""
from datetime import date, timedelta


def _easter(year):
    """Anonymous Gregorian algorithm — returns Easter Sunday."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def _nth_weekday(year, month, weekday, n):
    """nth <weekday> (0=Mon) of a month."""
    first = date(year, month, 1)
    offset = (weekday - first.weekday()) % 7
    return first + timedelta(days=offset + 7 * (n - 1))


def qld_holidays(year):
    """Return {date: name} for QLD state-wide public holidays."""
    easter = _easter(year)
    return {
        date(year, 1, 1): "New Year's Day",
        date(year, 1, 26): "Australia Day",
        easter - timedelta(days=2): "Good Friday",
        easter - timedelta(days=1): "Easter Saturday",
        easter: "Easter Sunday",
        easter + timedelta(days=1): "Easter Monday",
        date(year, 4, 25): "Anzac Day",
        _nth_weekday(year, 5, 0, 1): "Labour Day",
        _nth_weekday(year, 10, 0, 1): "King's Birthday",
        date(year, 12, 25): "Christmas Day",
        date(year, 12, 26): "Boxing Day",
    }


def holidays_between(start, end):
    """Return {date: name} for all QLD holidays within [start, end]."""
    out = {}
    for year in range(start.year, end.year + 1):
        for d, name in qld_holidays(year).items():
            if start <= d <= end:
                out[d] = name
    return out
