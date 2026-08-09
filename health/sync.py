from datetime import date, timedelta, datetime
from decimal import Decimal
from django.utils.timezone import make_aware
from .client.garmin import get_client
from .models import DailyStats, Activity


def sync_daily_stats(days_back=7):
    client = get_client()
    today = date.today()

    for i in range(days_back):
        day = today - timedelta(days=i)
        day_str = day.isoformat()

        stats = client.get_stats(day_str) or {}
        body = client.get_body_composition(day_str) or {}
        sleep = client.get_sleep_data(day_str) or {}

        weight_g = (body.get('totalAverage') or {}).get('weight')
        sleep_seconds = (sleep.get('dailySleepDTO') or {}).get('sleepTimeSeconds')

        DailyStats.objects.update_or_create(
            date=day,
            defaults={
                'steps': stats.get('totalSteps'),
                'calories': stats.get('totalKilocalories'),
                'resting_heart_rate': stats.get('restingHeartRate'),
                'sleep_seconds': sleep_seconds,
                'weight_kg': Decimal(str(weight_g / 1000)) if weight_g else None,
            }
        )


def sync_activities(limit=10):
    client = get_client()
    activities = client.get_activities(0, limit)

    for a in activities:
        start_time_str = a.get('startTimeLocal')
        if not start_time_str:
            continue

        Activity.objects.update_or_create(
            garmin_id=a['activityId'],
            defaults={
                'name': a.get('activityName', ''),
                'activity_type': (a.get('activityType') or {}).get('typeKey', ''),
                'start_time': make_aware(datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')),
                'duration_seconds': int(a.get('duration') or 0),
                'distance_m': a.get('distance'),
                'calories': a.get('calories'),
            }
        )
