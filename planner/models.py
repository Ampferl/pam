from django.db import models
from django.core.exceptions import ValidationError

class Category(models.Model):
    name = models.CharField(max_length=256)
    color_hex = models.CharField(
        max_length=7,
        default='#007bff',
        help_text='Hex Farb Code.'
    )

    class Meta:
        verbose_name_plural = 'Kategorien'

    def __str__(self):
        return self.name


class Event(models.Model):
    title = models.CharField(max_length=256)
    description = models.TextField(blank=True, help_text="Optionale Event Beschreibung.")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        if self.start_time and self.end_time:
            if self.start_time > self.end_time:
                raise ValidationError("Die Endzeit eines Events kann nicht vor der Startzeit sein!")

    def __str__(self):
        return f"{self.title} ({self.start_time.date()})"
