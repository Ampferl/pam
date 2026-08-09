from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from planner.utils import get_upcoming_events, get_recent_events


@login_required
def index_view(request):
    upcoming = get_upcoming_events(request.user, limit=3)
    recent_activities = get_recent_events(request.user, limit=3, source_keys={'health.activity'})

    context = {
        'upcoming_events': upcoming,
        'recent_activities': recent_activities,
    }
    return render(request, "core/index.html", context)


# NOTE: This is a PoC
@login_required
def management_view(request):
    context = {
        "switches": [
            {"id": 0, "name": "Demo 1", "active": False},
            {"id": 1, "name": "Demo 2", "active": True},
            {"id": 2, "name": "Demo 3", "active": False},
        ]
    }
    return render(request, "core/management/index.html", context)



