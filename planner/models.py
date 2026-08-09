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


class Contact(models.Model):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150, blank=True)

    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    birthday = models.DateField(null=True, blank=True)

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Kontakt'
        verbose_name_plural = 'Kontakte'
        ordering = ['first_name', 'last_name']

    def __str__(self):
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name

    @property
    def color(self):
        if not self.id:
            return 'primary'
        colors = ['primary', 'success', 'danger', 'warning', 'info', 'secondary']
        return colors[self.id % len(colors)]

    @property
    def initials(self):
        first = self.first_name[0].upper() if self.first_name else ''
        last = self.last_name[0].upper() if self.last_name else ''
        return f"{first}{last}"

