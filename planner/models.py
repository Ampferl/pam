from django.db import models
from django.utils import timezone
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


# Tasks
class TaskList(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    color_hex = models.CharField(max_length=7, default='#6c757d', help_text='Hex Farb Code.')
    due_date = models.DateTimeField(null=True, blank=True)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Aufgabenliste'
        verbose_name_plural = 'Aufgabenlisten'
        ordering = ['is_archived', '-created_at']

    def __str__(self):
        return self.name

class TaskGroup(models.Model):
    task_list = models.ForeignKey(TaskList, on_delete=models.CASCADE, related_name='groups')
    name = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Aufgabengruppe'
        verbose_name_plural = 'Aufgabengruppen'
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.task_list.name} / {self.name}"

class Task(models.Model):
    task_list = models.ForeignKey(TaskList, on_delete=models.CASCADE, related_name='tasks')
    group = models.ForeignKey(TaskGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subtasks')

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    is_done = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Aufgabe'
        verbose_name_plural = 'Aufgaben'
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        if self.parent_id:
            if self.parent_id == self.id:
                raise ValidationError("Eine Aufgabe kann nicht ihre eigene Unteraufgabe sein.")
            if self.parent.task_list_id != self.task_list_id:
                raise ValidationError("Unteraufgaben müssen zur selben Aufgabenliste gehören wie die übergeordnete Aufgabe.")
        if self.group_id and self.group.task_list_id != self.task_list_id:
            raise ValidationError("Die Gruppe muss zur selben Aufgabenliste gehören wie die Aufgabe.")

    def save(self, *args, **kwargs):
        if self.is_done and self.completed_at is None:
            self.completed_at = timezone.now()
        elif not self.is_done:
            self.completed_at = None
        super().save(*args, **kwargs)

    @property
    def depth(self):
        depth = 0
        node = self
        while node.parent_id:
            depth += 1
            node = node.parent
        return depth
