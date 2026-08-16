from django.contrib import admin
from .models import KnowledgeItem


@admin.register(KnowledgeItem)
class KnowledgeItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'item_type', 'parent', 'updated_at')
    list_filter = ('item_type',)
    search_fields = ('name', 'content')
    readonly_fields = ('created_at', 'updated_at')
