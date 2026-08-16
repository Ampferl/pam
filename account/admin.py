from django.contrib import admin
from .models import CalendarFeedToken


@admin.register(CalendarFeedToken)
class CalendarFeedTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    readonly_fields = ('token', 'created_at')
