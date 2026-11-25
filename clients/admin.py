from django.contrib import admin

from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("full_name", "client_type", "tax_id", "phone", "email")
    list_filter = ("client_type",)
    search_fields = ("full_name", "tax_id", "registration_number", "phone", "email")
