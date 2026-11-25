from django import forms
from django.forms import inlineformset_factory

from .models import Case, CaseMaterial, CaseParticipant, web_url_validator


class BootstrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            widget.attrs["class"] = (
                "form-select" if isinstance(widget, forms.Select) else "form-control"
            )


class CaseForm(BootstrapModelForm):
    class Meta:
        model = Case
        fields = ("number", "title", "client", "court_name", "court_details", "judge", "stage")
        widgets = {
            "court_details": forms.Textarea(attrs={"rows": 3}),
        }
        help_texts = {
            "court_details": "Например, адрес суда, зал заседания или телефон канцелярии.",
        }


class CaseParticipantForm(BootstrapModelForm):
    class Meta:
        model = CaseParticipant
        fields = ("name", "role", "client")


class CaseMaterialForm(BootstrapModelForm):
    url = forms.URLField(
        label="Ссылка",
        max_length=2048,
        assume_scheme="https",
        validators=[web_url_validator],
        widget=forms.URLInput(attrs={"placeholder": "https://"}),
    )

    class Meta:
        model = CaseMaterial
        fields = ("title", "url")


ParticipantFormSet = inlineformset_factory(
    Case, CaseParticipant, form=CaseParticipantForm, extra=1, max_num=100, validate_max=True
)
MaterialFormSet = inlineformset_factory(
    Case, CaseMaterial, form=CaseMaterialForm, extra=1, max_num=100, validate_max=True
)
