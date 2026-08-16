from django.urls import reverse
from core.calendar_sources import CalendarItem, CalendarSubgroup, register
from .models import Event, Contact, Category, TaskList, TaskGroup, Task

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


class TaskSource:
    key = "planner.task"
    label = "Aufgaben"

    def get_items(self, start, end, user):
        items = []

        lists = TaskList.objects.filter(
            is_archived=False, due_date__date__gte=start, due_date__date__lte=end,
        )
        for tl in lists:
            items.append(self._item(tl.due_date, f"📋 {tl.name}", tl.color_hex, tl.id))

        groups = TaskGroup.objects.filter(
            task_list__is_archived=False, due_date__date__gte=start, due_date__date__lte=end,
        ).select_related('task_list')
        for g in groups:
            items.append(self._item(g.due_date, f"🗂 {g.name}", g.task_list.color_hex, g.task_list_id))

        tasks = Task.objects.filter(
            task_list__is_archived=False, is_done=False,
            due_date__date__gte=start, due_date__date__lte=end,
        ).select_related('task_list')
        for t in tasks:
            items.append(self._item(t.due_date, f"✅ {t.title}", t.task_list.color_hex, t.task_list_id))

        return items

    def _item(self, due, title, color, task_list_id):
        return CalendarItem(
            title=title, date=due.date(), all_day=False,
            start_time=due.time(), end_time=due.time(),
            color=color, url=reverse('planner:tasklist_detail', args=[task_list_id]),
            source_key=self.key, subgroup_key=f'tasklist-{task_list_id}',
        )

    def get_subgroups(self):
        return [
            CalendarSubgroup(key=f'tasklist-{tl.id}', label=tl.name, color=tl.color_hex)
            for tl in TaskList.objects.filter(is_archived=False)
        ]


register(EventSource())
register(BirthdaySource())
register(TaskSource())
