from django.urls import reverse
from core.calendar_sources import CalendarItem, CalendarSubgroup, register
from .models import Event, Contact, Category

class EventSource:
    key = "planner.event"
    label = "Termine"

    def get_items(self, start, end, user):
        qs = Event.objects.filter(start_time__date__lte=end, end_time__date__gte=start).select_related('category')
        return [
            CalendarItem(
                title=e.title, date=e.start_time.date(), all_day=False,
                start_time=e.start_time.time(), end_time=e.end_time.time(),
                color=e.category.color_hex if e.category else "#0d6efd",
                url=reverse('planner:event_detail', args=[e.id]), source_key=self.key,
                subgroup_key=f'category-{e.category_id}' if e.category_id else '',
                description=e.description,
            ) for e in qs
        ]

    def get_subgroups(self):
        return [
            CalendarSubgroup(key=f'category-{c.id}', label=c.name, color=c.color_hex)
            for c in Category.objects.all()
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
                    occ = contact.birthday.replace(year=year, day=28)
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
