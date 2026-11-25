from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Client",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "client_type",
                    models.CharField(
                        choices=[
                            ("person", "Физическое лицо"),
                            ("sole_proprietor", "Индивидуальный предприниматель"),
                            ("company", "Юридическое лицо"),
                        ],
                        max_length=20,
                        verbose_name="Тип клиента",
                    ),
                ),
                ("full_name", models.CharField(max_length=255, verbose_name="ФИО или наименование")),
                ("tax_id", models.CharField(blank=True, max_length=12, verbose_name="ИНН")),
                ("registration_number", models.CharField(blank=True, max_length=15, verbose_name="ОГРН или ОГРНИП")),
                ("kpp", models.CharField(blank=True, max_length=9, verbose_name="КПП")),
                ("contact_name", models.CharField(blank=True, max_length=255, verbose_name="Контактное лицо")),
                ("phone", models.CharField(blank=True, max_length=32, verbose_name="Телефон")),
                ("email", models.EmailField(blank=True, max_length=254, verbose_name="Электронная почта")),
                ("address", models.CharField(blank=True, max_length=350, verbose_name="Адрес")),
                ("notes", models.TextField(blank=True, verbose_name="Заметки")),
            ],
            options={
                "verbose_name": "клиент",
                "verbose_name_plural": "клиенты",
                "ordering": ["full_name", "pk"],
            },
        ),
    ]
