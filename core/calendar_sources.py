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


class CalendarSource(Protocol):
    key: str
    label: str
    def get_items(self, start: date, end: date, user) -> list[CalendarItem]: ...


_registry: list[CalendarSource] = []

def register(source: CalendarSource) -> None:
    _registry.append(source)

def get_all_items(start: date, end: date, user) -> list[CalendarItem]:
    items = []
    for source in _registry:
        items.extend(source.get_items(start, end, user))
    return items

def get_sources() -> list[CalendarSource]:
    return list(_registry)
