import json
from datetime import date, timedelta
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import DailyStats, Activity
from .sync import sync_daily_stats, sync_activities


WEEKDAY_LABELS = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']


@login_required
def index_view(request):
    today = date.today()
    last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    stats_by_date = {
        s.date: s for s in DailyStats.objects.filter(date__gte=last_7_days[0], date__lte=today)
    }

    context = {
        'latest_stats': DailyStats.objects.first(),
        'recent_activities': Activity.objects.all()[:5],
        'chart_labels': json.dumps([WEEKDAY_LABELS[d.weekday()] for d in last_7_days]),
        'chart_steps': json.dumps([
            stats_by_date[d].steps if d in stats_by_date and stats_by_date[d].steps else 0
            for d in last_7_days
        ]),
    }
    return render(request, "health/index.html", context)


@login_required
@require_POST
def garmin_sync_view(request):
    try:
        sync_daily_stats(days_back=7)
        sync_activities(limit=10)
        messages.success(request, "Garmin-Daten erfolgreich synchronisiert.")
    except Exception as e:
        messages.error(request, f"Garmin-Sync fehlgeschlagen: {e}")
    return redirect('health:overview')


