from django.contrib import admin
from .models import Contact, Category, Event, TaskList, TaskGroup, Task   # replace existing import line

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


class TaskGroupInline(admin.TabularInline):
    model = TaskGroup
    extra = 0
    fields = ('name', 'order', 'due_date')


class TaskInline(admin.TabularInline):
    model = Task
    fk_name = 'task_list'
    extra = 0
    fields = ('title', 'group', 'parent', 'due_date', 'is_done', 'order')
    autocomplete_fields = ('group', 'parent')


@admin.register(TaskList)
class TaskListAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_archived', 'due_date', 'color_hex')
    list_filter = ('is_archived',)
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [TaskGroupInline, TaskInline]


@admin.register(TaskGroup)
class TaskGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'task_list', 'due_date', 'order')
    list_filter = ('task_list',)
    search_fields = ('name',)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'task_list', 'group', 'parent', 'due_date', 'is_done')
    list_filter = ('task_list', 'is_done')
    search_fields = ('title', 'description')
    readonly_fields = ('completed_at', 'created_at', 'updated_at')
    autocomplete_fields = ('group', 'parent')
