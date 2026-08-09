from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import DailyStats, Activity
from .sync import sync_daily_stats, sync_activities


@login_required
def index_view(request):
    context = {
        'latest_stats': DailyStats.objects.first(),
        'recent_activities': Activity.objects.all()[:5],
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


