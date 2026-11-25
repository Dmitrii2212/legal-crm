from django.db import models
from django.urls import reverse


class Task(models.Model):
    class Kind(models.TextChoices):
        TASK = "task", "Задача"
        DEADLINE = "deadline", "Контрольный срок"

    class Status(models.TextChoices):
        OPEN = "open", "К выполнению"
        IN_PROGRESS = "in_progress", "В работе"
        DONE = "done", "Выполнено"

    case = models.ForeignKey(
        "cases.Case",
        on_delete=models.CASCADE,
        related_name="tasks",
        verbose_name="Судебное дело",
    )
    title = models.CharField("Название", max_length=255)
    kind = models.CharField("Тип", max_length=16, choices=Kind.choices, default=Kind.TASK)
    due_at = models.DateTimeField("Дата и время", db_index=True)
    status = models.CharField(
        "Статус", max_length=16, choices=Status.choices, default=Status.OPEN
    )
    description = models.TextField("Описание", blank=True)

    class Meta:
        ordering = ("due_at", "pk")
        verbose_name = "задача или срок"
        verbose_name_plural = "задачи и сроки"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("tasks:detail", args=[self.pk])
