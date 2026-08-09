from django.db import models


class KnowledgeItem(models.Model):
    ITEM_TYPES = (
        ('folder', 'Ordner'),
        ('file', 'Notiz'),
    )

    name = models.CharField(max_length=255)
    item_type = models.CharField(max_length=10, choices=ITEM_TYPES, default='file')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Knowledge Base Item'
        verbose_name_plural = 'Knowledge Base Items'
        ordering = ['name']

    def __str__(self):
        return f"[{self.get_item_type_display()}] {self.name}"

