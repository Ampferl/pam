from core.calendar_sources import CalendarItem, register
from .models import Event, Contact

class EventSource:
    key = "planner.event"
    label = "Termine"

    def get_items(self, start, end, user):
        qs = Event.objects.filter(start_time__date__lte=end, end_time__date__gte=start)
        return [
            CalendarItem(
                title=e.title, date=e.start_time.date(), all_day=False,
                start_time=e.start_time.time(), end_time=e.end_time.time(),
                color=e.category.color_hex if e.category else "#0d6efd",
                url=f"/planner/event/{e.id}/", source_key=self.key,
            ) for e in qs
        ]

class BirthdaySource:
    key = "planner.birthday"
    label = "Geburtstage"

    def get_items(self, start, end, user):
        items = []
        for contact in Contact.objects.exclude(birthday=None):
            for year in range(start.year, end.year + 1):
                try:
                    occ = contact.birthday.replace(year=year)
                except ValueError:
                    occ = contact.birthday.replace(year=year, day=28)  # Feb 29 fallback
                if start <= occ <= end:
                    age = year - contact.birthday.year
                    items.append(CalendarItem(
                        title=f"🎂 {contact} ({age})", date=occ,
                        color="#e83e8c", url=f"/planner/contacts/{contact.id}",
                        source_key=self.key,
                    ))
        return items

register(EventSource())
register(BirthdaySource())
