from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "case", "kind", "due_at", "status")
    list_filter = ("kind", "status")
    list_select_related = ("case",)
    search_fields = ("title", "case__number")
    date_hierarchy = "due_at"
