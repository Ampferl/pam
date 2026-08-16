from django.contrib import admin
from .models import DailyStats, Activity


@admin.register(DailyStats)
class DailyStatsAdmin(admin.ModelAdmin):
    list_display = ('date', 'steps', 'calories', 'resting_heart_rate', 'sleep_hours', 'weight_kg', 'body_fat_percentage')
    list_filter = ('date',)
    search_fields = ('date',)
    readonly_fields = ('synced_at',)
    date_hierarchy = 'date'


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'activity_type', 'start_time', 'duration_minutes', 'distance_km', 'calories')
    list_filter = ('activity_type',)
    search_fields = ('name', 'activity_type')
    date_hierarchy = 'start_time'
