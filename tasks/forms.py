from datetime import UTC

from django import forms
from django.utils import timezone

from cases.models import Case

from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ("case", "title", "kind", "due_at", "status", "description")
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "case": forms.Select(attrs={"class": "form-select"}),
            "kind": forms.Select(attrs={"class": "form-select"}),
            "due_at": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M",
                attrs={"class": "form-control", "type": "datetime-local"},
            ),
            "status": forms.Select(attrs={"class": "form-select"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }
        help_texts = {"due_at": "Московское время (МСК)."}

    def __init__(self, *args, fixed_case=None, **kwargs):
        super().__init__(*args, **kwargs)
        if fixed_case is None:
            self.fields["case"].queryset = Case.objects.order_by("number", "title")
        else:
            self.instance.case = fixed_case
            self.fields.pop("case")

    def clean_due_at(self):
        due_at = self.cleaned_data["due_at"]
        try:
            due_at.astimezone(UTC)
            return timezone.localtime(due_at)
        except OverflowError as error:
            raise forms.ValidationError("Укажите дату и время в допустимом диапазоне.") from error
