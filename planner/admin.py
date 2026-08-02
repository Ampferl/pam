from django.contrib import admin
from .models import Category, Event

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'color_hex')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'end_time', 'category')
    list_filter = ('category', 'start_time')
    search_fields = ('title', 'description')
