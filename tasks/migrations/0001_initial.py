import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("cases", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Task",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("title", models.CharField(max_length=255, verbose_name="Название")),
                (
                    "kind",
                    models.CharField(
                        choices=[("task", "Задача"), ("deadline", "Контрольный срок")],
                        default="task",
                        max_length=16,
                        verbose_name="Тип",
                    ),
                ),
                ("due_at", models.DateTimeField(db_index=True, verbose_name="Дата и время")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("open", "К выполнению"),
                            ("in_progress", "В работе"),
                            ("done", "Выполнено"),
                        ],
                        default="open",
                        max_length=16,
                        verbose_name="Статус",
                    ),
                ),
                ("description", models.TextField(blank=True, verbose_name="Описание")),
                (
                    "case",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tasks",
                        to="cases.case",
                        verbose_name="Судебное дело",
                    ),
                ),
            ],
            options={
                "verbose_name": "задача или срок",
                "verbose_name_plural": "задачи и сроки",
                "ordering": ("due_at", "pk"),
            },
        ),
    ]
