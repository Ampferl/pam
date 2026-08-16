import secrets
from django.conf import settings
from django.db import models


def generate_token():
    return secrets.token_urlsafe(32)


class CalendarFeedToken(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='calendar_feed_token')
    token = models.CharField(max_length=64, unique=True, default=generate_token)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feed-Token für {self.user}"
