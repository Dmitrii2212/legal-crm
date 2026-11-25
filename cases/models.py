from django.core.validators import URLValidator
from django.db import models
from django.urls import reverse


web_url_validator = URLValidator(schemes=("http", "https"))


class Case(models.Model):
    class Stage(models.TextChoices):
        PREPARATION = "preparation", "Подготовка"
        FIRST_INSTANCE = "first_instance", "Первая инстанция"
        APPEAL = "appeal", "Апелляция"
        CASSATION = "cassation", "Кассация"
        SUPERVISION = "supervision", "Надзор"
        ENFORCEMENT = "enforcement", "Исполнение"
        FINISHED = "finished", "Завершено"

    number = models.CharField("Номер дела", max_length=64, db_index=True)
    title = models.CharField("Название", max_length=255)
    client = models.ForeignKey(
        "clients.Client",
        verbose_name="Клиент",
        on_delete=models.PROTECT,
        related_name="cases",
    )
    court_name = models.CharField("Наименование суда", max_length=255)
    court_details = models.TextField("Реквизиты суда", blank=True)
    judge = models.CharField("Судья", max_length=150, blank=True)
    stage = models.CharField(
        "Стадия",
        max_length=20,
        choices=Stage,
        default=Stage.FIRST_INSTANCE,
        db_index=True,
    )
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Изменено", auto_now=True)

    class Meta:
        verbose_name = "Судебное дело"
        verbose_name_plural = "Судебные дела"
        ordering = ("-updated_at", "-pk")

    def __str__(self):
        return f"{self.number} · {self.title}"

    def get_absolute_url(self):
        return reverse("cases:detail", kwargs={"pk": self.pk})


class CaseParticipant(models.Model):
    class Role(models.TextChoices):
        CLAIMANT = "claimant", "Истец"
        RESPONDENT = "respondent", "Ответчик"
        APPLICANT = "applicant", "Заявитель"
        INTERESTED_PARTY = "interested_party", "Заинтересованное лицо"
        THIRD_PARTY = "third_party", "Третье лицо"
        REPRESENTATIVE = "representative", "Представитель"
        OTHER = "other", "Другая роль"

    case = models.ForeignKey(
        Case,
        verbose_name="Дело",
        on_delete=models.CASCADE,
        related_name="participants",
    )
    name = models.CharField("Имя или наименование", max_length=255)
    role = models.CharField("Роль", max_length=20, choices=Role)
    client = models.ForeignKey(
        "clients.Client",
        verbose_name="Карточка клиента",
        on_delete=models.SET_NULL,
        related_name="case_participations",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Участник дела"
        verbose_name_plural = "Участники дела"
        ordering = ("pk",)

    def __str__(self):
        return f"{self.name} · {self.get_role_display()}"


class CaseMaterial(models.Model):
    case = models.ForeignKey(
        Case,
        verbose_name="Дело",
        on_delete=models.CASCADE,
        related_name="materials",
    )
    title = models.CharField("Название материала", max_length=255)
    url = models.URLField("Ссылка", max_length=2048, validators=[web_url_validator])

    class Meta:
        verbose_name = "Материал дела"
        verbose_name_plural = "Материалы дела"
        ordering = ("pk",)

    def __str__(self):
        return self.title
