from django.contrib import admin
from .models import Task, Category

# Method 1: Using decorators (recommended)
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'completed', 'priority', 'due_date', 'created_date']
    list_filter = ['completed', 'priority', 'created_date', 'category']
    search_fields = ['title', 'description']
    readonly_fields = ['created_date']
    fieldsets = [
        (None, {'fields': ['user', 'title', 'description']}),
        ('Status', {'fields': ['completed', 'priority']}),
        ('Dates', {'fields': ['due_date', 'reminder', 'created_date']}),
        ('Category', {'fields': ['category']}),
    ]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'user']
    list_filter = ['user']
    search_fields = ['name']
    fields = ['name', 'color', 'user']