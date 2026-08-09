from datetime import timedelta, datetime
from django.utils import timezone
from core.calendar_sources import get_all_items


GERMAN_MONTHS_SHORT = [
    "", "JAN", "FEB", "MÄR", "APR", "MAI", "JUN",
    "JUL", "AUG", "SEP", "OKT", "NOV", "DEZ"
]


def _filter_by_subgroup(items, subgroup_keys):
    if subgroup_keys is None:
        return items
    subgroup_keys = set(subgroup_keys)
    return [i for i in items if (i.source_key, i.subgroup_key) in subgroup_keys]


def _serialize(item):
    time_str = "Ganztägig" if item.all_day else f"{item.start_time.strftime('%H:%M')} - {item.end_time.strftime('%H:%M')} Uhr"
    return {
        'title': item.title,
        'day': item.date.day,
        'month': GERMAN_MONTHS_SHORT[item.date.month],
        'time_str': time_str,
        'color': item.color,
        'url': item.url,
    }


def get_upcoming_events(user, limit=3, source_keys=None, subgroup_keys=None):
    now = timezone.localtime(timezone.now())
    today = now.date()
    horizon = today + timedelta(days=90)

    items = get_all_items(today, horizon, user, source_keys=source_keys)
    items = _filter_by_subgroup(items, subgroup_keys)

    upcoming = []
    for item in items:
        end_time = item.end_time or item.start_time or datetime.max.time()
        item_end = timezone.make_aware(datetime.combine(item.date, end_time))
        if item_end >= now:
            upcoming.append(item)

    upcoming.sort(key=lambda i: (i.date, i.start_time or datetime.min.time()))
    return [_serialize(i) for i in upcoming[:limit]]


def get_recent_events(user, limit=3, source_keys=None, subgroup_keys=None):
    now = timezone.localtime(timezone.now())
    today = now.date()
    horizon = today - timedelta(days=90)

    items = get_all_items(horizon, today, user, source_keys=source_keys)
    items = _filter_by_subgroup(items, subgroup_keys)

    recent = []
    for item in items:
        end_time = item.end_time or item.start_time or datetime.max.time()
        item_end = timezone.make_aware(datetime.combine(item.date, end_time))
        if item_end < now:
            recent.append(item)

    recent.sort(key=lambda i: (i.date, i.start_time or datetime.min.time()), reverse=True)
    return [_serialize(i) for i in recent[:limit]]

