from datetime import timedelta
from django.urls import reverse
from core.calendar_sources import CalendarItem, CalendarSubgroup, register
from .models import Activity


ACTIVITY_TYPE_COLORS = {
    'running': '#fd7e14',
    'cycling': '#20c997',
    'strength_training': '#6f42c1',
    'walking': '#0dcaf0',
    'swimming': '#0d6efd',
}
DEFAULT_ACTIVITY_COLOR = '#6c757d'


class ActivitySource:
    key = "health.activity"
    label = "Aktivitäten"

    def get_items(self, start, end, user):
        qs = Activity.objects.filter(start_time__date__gte=start, start_time__date__lte=end)
        return [
            CalendarItem(
                title=a.name,
                date=a.start_time.date(),
                all_day=False,
                start_time=a.start_time.time(),
                end_time=(a.start_time + timedelta(seconds=a.duration_seconds)).time(),
                color=ACTIVITY_TYPE_COLORS.get(a.activity_type, DEFAULT_ACTIVITY_COLOR),
                url=reverse('health:overview'),
                source_key=self.key,
                subgroup_key=f'activity-type-{a.activity_type}' if a.activity_type else '',
            ) for a in qs
        ]

    def get_subgroups(self):
        types = (
            Activity.objects.exclude(activity_type='')
            .values_list('activity_type', flat=True)
            .distinct()
            .order_by('activity_type')
        )
        return [
            CalendarSubgroup(
                key=f'activity-type-{t}',
                label=t.replace('_', ' ').title(),
                color=ACTIVITY_TYPE_COLORS.get(t, DEFAULT_ACTIVITY_COLOR),
            )
            for t in types
        ]


register(ActivitySource())
