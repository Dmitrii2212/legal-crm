from django.contrib import admin

from .models import Case, CaseMaterial, CaseParticipant


class CaseParticipantInline(admin.TabularInline):
    model = CaseParticipant
    extra = 0


class CaseMaterialInline(admin.TabularInline):
    model = CaseMaterial
    extra = 0


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ("number", "title", "client", "court_name", "stage", "updated_at")
    list_filter = ("stage",)
    search_fields = ("number", "title", "client__full_name", "court_name", "judge")
    list_select_related = ("client",)
    inlines = (CaseParticipantInline, CaseMaterialInline)
