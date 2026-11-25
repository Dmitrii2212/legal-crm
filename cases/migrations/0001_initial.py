import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("clients", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Case",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("number", models.CharField(db_index=True, max_length=64, verbose_name="Номер дела")),
                ("title", models.CharField(max_length=255, verbose_name="Название")),
                ("court_name", models.CharField(max_length=255, verbose_name="Наименование суда")),
                ("court_details", models.TextField(blank=True, verbose_name="Реквизиты суда")),
                ("judge", models.CharField(blank=True, max_length=150, verbose_name="Судья")),
                (
                    "stage",
                    models.CharField(
                        choices=[
                            ("preparation", "Подготовка"),
                            ("first_instance", "Первая инстанция"),
                            ("appeal", "Апелляция"),
                            ("cassation", "Кассация"),
                            ("supervision", "Надзор"),
                            ("enforcement", "Исполнение"),
                            ("finished", "Завершено"),
                        ],
                        db_index=True,
                        default="first_instance",
                        max_length=20,
                        verbose_name="Стадия",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создано")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Изменено")),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="cases",
                        to="clients.client",
                        verbose_name="Клиент",
                    ),
                ),
            ],
            options={
                "verbose_name": "Судебное дело",
                "verbose_name_plural": "Судебные дела",
                "ordering": ("-updated_at", "-pk"),
            },
        ),
        migrations.CreateModel(
            name="CaseMaterial",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255, verbose_name="Название материала")),
                (
                    "url",
                    models.URLField(
                        max_length=2048,
                        validators=[django.core.validators.URLValidator(schemes=("http", "https"))],
                        verbose_name="Ссылка",
                    ),
                ),
                (
                    "case",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="materials",
                        to="cases.case",
                        verbose_name="Дело",
                    ),
                ),
            ],
            options={
                "verbose_name": "Материал дела",
                "verbose_name_plural": "Материалы дела",
                "ordering": ("pk",),
            },
        ),
        migrations.CreateModel(
            name="CaseParticipant",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, verbose_name="Имя или наименование")),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("claimant", "Истец"),
                            ("respondent", "Ответчик"),
                            ("applicant", "Заявитель"),
                            ("interested_party", "Заинтересованное лицо"),
                            ("third_party", "Третье лицо"),
                            ("representative", "Представитель"),
                            ("other", "Другая роль"),
                        ],
                        max_length=20,
                        verbose_name="Роль",
                    ),
                ),
                (
                    "case",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="participants",
                        to="cases.case",
                        verbose_name="Дело",
                    ),
                ),
                (
                    "client",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="case_participations",
                        to="clients.client",
                        verbose_name="Карточка клиента",
                    ),
                ),
            ],
            options={
                "verbose_name": "Участник дела",
                "verbose_name_plural": "Участники дела",
                "ordering": ("pk",),
            },
        ),
    ]
