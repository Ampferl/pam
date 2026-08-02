from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from planner.utils import get_upcoming_events


@login_required
def index_view(request):
    upcoming = get_upcoming_events(limit=3)

    context = {
        'upcoming_events': upcoming,
    }
    return render(request, "core/index.html", context)

