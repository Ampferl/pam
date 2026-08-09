from dataclasses import dataclass
from datetime import date, time
from typing import Optional, Protocol


@dataclass
class CalendarItem:
    title: str
    date: date
    all_day: bool = True
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    color: str = '#6c757d'
    url: str = ''
    source_key: str = ''
    subgroup_key: str = ''
    description: str = ''


@dataclass
class CalendarSubgroup:
    key: str
    label: str
    color: str = '#6c757d'


class CalendarSource(Protocol):
    key: str
    label: str
    def get_items(self, start: date, end: date, user) -> list[CalendarItem]: ...


_registry: list[CalendarSource] = []

def register(source: CalendarSource) -> None:
    _registry.append(source)

def get_all_items(start: date, end: date, user, source_keys=None) -> list[CalendarItem]:
    items = []
    for source in _registry:
        if source_keys is not None and source.key not in source_keys:
            continue
        items.extend(source.get_items(start, end, user))
    return items

def get_sources() -> list[CalendarSource]:
    return list(_registry)

def get_source_subgroups(source: CalendarSource) -> list[CalendarSubgroup]:
    getter = getattr(source, 'get_subgroups', None)
    return getter() if getter else []
