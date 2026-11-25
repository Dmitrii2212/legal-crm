import re

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse


class Client(models.Model):
    class Type(models.TextChoices):
        PERSON = "person", "Физическое лицо"
        SOLE_PROPRIETOR = "sole_proprietor", "Индивидуальный предприниматель"
        COMPANY = "company", "Юридическое лицо"

    client_type = models.CharField("Тип клиента", max_length=20, choices=Type.choices)
    full_name = models.CharField("ФИО или наименование", max_length=255)
    tax_id = models.CharField("ИНН", max_length=12, blank=True)
    registration_number = models.CharField("ОГРН или ОГРНИП", max_length=15, blank=True)
    kpp = models.CharField("КПП", max_length=9, blank=True)
    contact_name = models.CharField("Контактное лицо", max_length=255, blank=True)
    phone = models.CharField("Телефон", max_length=32, blank=True)
    email = models.EmailField("Электронная почта", blank=True)
    address = models.CharField("Адрес", max_length=350, blank=True)
    notes = models.TextField("Заметки", blank=True)

    class Meta:
        verbose_name = "клиент"
        verbose_name_plural = "клиенты"
        ordering = ["full_name", "pk"]

    def __str__(self):
        return self.full_name

    def get_absolute_url(self):
        return reverse("clients:detail", kwargs={"pk": self.pk})

    def clean(self):
        super().clean()
        errors = {}

        if self.tax_id:
            expected_length = 10 if self.client_type == self.Type.COMPANY else 12
            if not re.fullmatch(rf"[0-9]{{{expected_length}}}", self.tax_id):
                errors["tax_id"] = f"ИНН должен содержать {expected_length} цифр."

        if self.registration_number:
            if self.client_type == self.Type.PERSON:
                errors["registration_number"] = "Укажите ОГРН или ОГРНИП только для организации или ИП."
            elif self.client_type == self.Type.COMPANY:
                if not re.fullmatch(r"[0-9]{13}", self.registration_number):
                    errors["registration_number"] = "ОГРН должен содержать 13 цифр."
            elif not re.fullmatch(r"[0-9]{15}", self.registration_number):
                errors["registration_number"] = "ОГРНИП должен содержать 15 цифр."

        if self.kpp:
            if self.client_type != self.Type.COMPANY:
                errors["kpp"] = "Укажите КПП только для юридического лица."
            elif not re.fullmatch(r"[0-9]{4}[0-9A-Z]{2}[0-9]{3}", self.kpp):
                errors["kpp"] = "Введите КПП из 9 знаков. На пятой и шестой позициях допустимы латинские заглавные буквы."

        if errors:
            raise ValidationError(errors)
