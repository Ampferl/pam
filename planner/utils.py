from django.utils import timezone
from .models import Event


def get_upcoming_events(limit=3):
    now = timezone.now()

    events = Event.objects.filter(
        end_time__gte=now
    ).select_related('category').order_by('start_time')[:limit]

    german_months_short = [
        "", "JAN", "FEB", "MÄR", "APR", "MAI", "JUN", 
        "JUL", "AUG", "SEP", "OKT", "NOV", "DEZ"
    ]

    upcoming_list = []
    for event in events:
        local_start = timezone.localtime(event.start_time)
        local_end = timezone.localtime(event.end_time)

        upcoming_list.append({
            'id': event.id,
            'title': event.title,
            'day': local_start.day,  # e.g., 14
            'month': german_months_short[local_start.month],  # e.g., 'OKT'
            'time_str': f"{local_start.strftime('%H:%M')} - {local_end.strftime('%H:%M')} Uhr",
            'color': event.category.color_hex if event.category else '#0d6efd',
        })

    return upcoming_list

