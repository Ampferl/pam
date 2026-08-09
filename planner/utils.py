from datetime import timedelta, datetime
from django.utils import timezone
from core.calendar_sources import get_all_items


def get_upcoming_events(user, limit=3):
    now = timezone.localtime(timezone.now())
    today = now.date()
    horizon = today + timedelta(days=90)

    items = get_all_items(today, horizon, user)

    upcoming = []
    for item in items:
        end_time = item.end_time or item.start_time or datetime.max.time()
        item_end = timezone.make_aware(datetime.combine(item.date, end_time))
        if item_end >= now:
            upcoming.append(item)

    upcoming.sort(key=lambda i: (i.date, i.start_time or datetime.min.time()))
    upcoming = upcoming[:limit]

    german_months_short = [
        "", "JAN", "FEB", "MÄR", "APR", "MAI", "JUN",
        "JUL", "AUG", "SEP", "OKT", "NOV", "DEZ"
    ]

    upcoming_list = []
    for item in upcoming:
        time_str = "Ganztägig" if item.all_day else f"{item.start_time.strftime('%H:%M')} - {item.end_time.strftime('%H:%M')} Uhr"
        upcoming_list.append({
            'title': item.title,
            'day': item.date.day,
            'month': german_months_short[item.date.month],
            'time_str': time_str,
            'color': item.color,
            'url': item.url,
        })

    return upcoming_list

