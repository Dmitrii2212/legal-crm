from django import forms

from .models import Client


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            "client_type",
            "full_name",
            "tax_id",
            "registration_number",
            "kpp",
            "contact_name",
            "phone",
            "email",
            "address",
            "notes",
        ]
        widgets = {
            "tax_id": forms.TextInput(attrs={"inputmode": "numeric"}),
            "registration_number": forms.TextInput(attrs={"inputmode": "numeric"}),
            "phone": forms.TextInput(attrs={"type": "tel"}),
            "notes": forms.Textarea(attrs={"rows": 4}),
        }
        help_texts = {
            "tax_id": "10 цифр для юридического лица, 12 для физического лица или ИП.",
            "registration_number": "13 цифр для юридического лица, 15 для ИП.",
            "kpp": "Заполняется для юридического лица.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-select" if isinstance(field.widget, forms.Select) else "form-control"
