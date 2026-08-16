from datetime import timedelta, datetime
from django.utils import timezone
from django.urls import reverse
from core.calendar_sources import get_all_items
from .models import TaskList, TaskGroup, Task


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


# Tasks
PINNED_TASKLIST_IDS = set()

def _due_time(due_date):
    return timezone.localtime(due_date).time() if due_date else None


def get_todays_tasks(user, pinned_tasklist_ids=None):
    today = timezone.localdate()
    pinned_ids = set(PINNED_TASKLIST_IDS if pinned_tasklist_ids is None else pinned_tasklist_ids)

    items = []
    seen_task_ids = set()

    for task_list in TaskList.objects.filter(is_archived=False, due_date__date=today):
        items.append({
            'kind': 'tasklist', 'title': task_list.name, 'color': task_list.color_hex,
            'url': reverse('planner:tasklist_detail', args=[task_list.id]),
            'due_time': _due_time(task_list.due_date), 'is_done': False, 'toggle_url': '',
            'pinned': task_list.id in pinned_ids,
        })

    for group in TaskGroup.objects.filter(task_list__is_archived=False, due_date__date=today).select_related('task_list'):
        items.append({
            'kind': 'taskgroup', 'title': f"{group.task_list.name} / {group.name}", 'color': group.task_list.color_hex,
            'url': reverse('planner:tasklist_detail', args=[group.task_list_id]),
            'due_time': _due_time(group.due_date), 'is_done': False, 'toggle_url': '',
            'pinned': group.task_list_id in pinned_ids,
        })

    due_today_tasks = Task.objects.filter(task_list__is_archived=False, due_date__date=today).select_related('task_list')
    for task in due_today_tasks:
        seen_task_ids.add(task.id)
        items.append({
            'kind': 'task', 'title': task.title, 'color': task.task_list.color_hex,
            'url': reverse('planner:tasklist_detail', args=[task.task_list_id]),
            'due_time': _due_time(task.due_date), 'is_done': task.is_done,
            'toggle_url': reverse('planner:task_update', args=[task.task_list_id, task.id]),
            'pinned': task.task_list_id in pinned_ids,
        })

    if pinned_ids:
        pinned_open_tasks = Task.objects.filter(
            task_list_id__in=pinned_ids, task_list__is_archived=False, is_done=False,
        ).exclude(id__in=seen_task_ids).select_related('task_list')
        for task in pinned_open_tasks:
            items.append({
                'kind': 'task', 'title': task.title, 'color': task.task_list.color_hex,
                'url': reverse('planner:tasklist_detail', args=[task.task_list_id]),
                'due_time': _due_time(task.due_date), 'is_done': task.is_done,
                'toggle_url': reverse('planner:task_update', args=[task.task_list_id, task.id]),
                'pinned': True,
            })

    items.sort(key=lambda i: (not i['pinned'], i['due_time'] or datetime.max.time()))
    return items


