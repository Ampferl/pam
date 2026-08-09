from django.db import models

class DailyStats(models.Model):
    date = models.DateField(unique=True)

    steps = models.PositiveIntegerField(null=True, blank=True)
    calories = models.PositiveIntegerField(null=True, blank=True)
    resting_heart_rate = models.PositiveSmallIntegerField(null=True, blank=True)
    sleep_seconds = models.PositiveIntegerField(null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    body_fat_percentage = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)

    synced_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Daily Stats'
        ordering = ['-date']

    def __str__(self):
        return f"{self.date}: {self.steps or 0} Schritte"

    @property
    def sleep_hours(self):
        return round(self.sleep_seconds / 3600, 1) if self.sleep_seconds else None


class Activity(models.Model):
    garmin_id = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=255)
    activity_type = models.CharField(max_length=100, blank=True)
    start_time = models.DateTimeField()
    duration_seconds = models.PositiveIntegerField(default=0)
    distance_m = models.FloatField(null=True, blank=True)
    calories = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.name} ({self.start_time.date()})"

    @property
    def duration_minutes(self):
        return round(self.duration_seconds / 60)

    @property
    def distance_km(self):
        return round(self.distance_m / 1000, 2) if self.distance_m else None
