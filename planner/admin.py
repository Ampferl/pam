from django.contrib import admin
from .models import Contact, Category, Event

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'color_hex')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'end_time', 'category')
    list_filter = ('category', 'start_time')
    search_fields = ('title', 'description')

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'birthday', 'get_initials', 'get_color')
    search_fields = ('first_name', 'last_name', 'email')
    readonly_fields = ('created_at', 'updated_at')
    list_filter = ('created_at',)

    def get_initials(self, obj):
        return obj.initials
    get_initials.short_description = 'Initialen'

    def get_color(self, obj):
        return obj.color
    get_color.short_description = 'Zugewiesene Farbe'
