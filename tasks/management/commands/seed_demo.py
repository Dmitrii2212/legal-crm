from datetime import datetime, time, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from django.utils import timezone

from cases.models import Case, CaseMaterial, CaseParticipant
from clients.models import Client
from tasks.models import Task

DEMO_USERNAME = "demo"
DEMO_PASSWORD = "legalcrm-demo"


class Command(BaseCommand):
    help = "Создаёт вымышленные карточки, учебное дело и задачи для знакомства с CRM."

    def add_arguments(self, parser):
        parser.add_argument(
            "--with-demo-user",
            action="store_true",
            help="Создать учебную учётную запись для локального режима SQLite.",
        )

    def handle(self, *args, **options):
        with_demo_user = options["with_demo_user"]
        sqlite_demo = getattr(settings, "DEMO_MODE", False) and connection.vendor == "sqlite"
        if with_demo_user and not sqlite_demo:
            raise CommandError("Учебная учётная запись доступна только в локальном режиме SQLite.")

        with transaction.atomic():
            demo_can_sign_in = with_demo_user and self.ensure_demo_user()
            if not with_demo_user or not Client.objects.exists():
                self.seed_records()

        self.stdout.write(self.style.SUCCESS("Учебные данные доступны в CRM."))
        if demo_can_sign_in:
            self.stdout.write(f"Login: {DEMO_USERNAME} | Password: {DEMO_PASSWORD}")
        elif with_demo_user:
            self.stdout.write("Учётная запись demo уже настроена. Используйте её текущий пароль.")

    def ensure_demo_user(self):
        user, created = get_user_model().objects.get_or_create(username=DEMO_USERNAME)
        if created:
            user.set_password(DEMO_PASSWORD)
            user.save(update_fields=["password"])
            return True
        return (
            user.is_active
            and not (user.is_staff or user.is_superuser)
            and user.check_password(DEMO_PASSWORD)
        )

    def seed_records(self):
        people = (
            (Client.Type.PERSON, "Пробная Анна Демовна", "person@example.com"),
            (Client.Type.SOLE_PROPRIETOR, "ИП Учебный Лев Макетович", "entrepreneur@example.com"),
            (Client.Type.COMPANY, 'ООО «Учебный контур»', "company@example.com"),
        )
        demo_clients = {}
        for client_type, full_name, email in people:
            demo_clients[client_type], _ = Client.objects.get_or_create(
                client_type=client_type,
                full_name=full_name,
                email=email,
                defaults={"notes": "Вымышленная карточка для демонстрации."},
            )

        client = demo_clients[Client.Type.COMPANY]
        case, _ = Case.objects.get_or_create(
            number="ДЕМО-01/2026",
            client=client,
            defaults={
                "title": "Спор об оплате учебной поставки",
                "court_name": "Демонстрационный арбитражный суд",
                "court_details": "Вымышленный адрес и реквизиты для примера.",
                "judge": "Проверочная М. Д.",
                "stage": Case.Stage.FIRST_INSTANCE,
            },
        )
        CaseParticipant.objects.get_or_create(
            case=case, name=client.full_name, role=CaseParticipant.Role.CLAIMANT,
            defaults={"client": client},
        )
        CaseParticipant.objects.get_or_create(
            case=case, name='ООО «Демо-поставщик»', role=CaseParticipant.Role.RESPONDENT,
        )
        CaseMaterial.objects.get_or_create(
            case=case, title="Демонстрационная ссылка", url="https://example.com/",
        )

        today = timezone.localdate()
        tasks = (
            ("Согласовать позицию с клиентом", Task.Kind.TASK, -1, time(16), Task.Status.OPEN),
            ("Проверить комплект документов", Task.Kind.TASK, 0, time(15), Task.Status.IN_PROGRESS),
            ("Представить письменные пояснения", Task.Kind.DEADLINE, 3, time(17), Task.Status.OPEN),
        )
        for title, kind, days, clock_time, status in tasks:
            due_at = timezone.make_aware(datetime.combine(today + timedelta(days=days), clock_time))
            Task.objects.get_or_create(
                case=case, title=title,
                defaults={"kind": kind, "due_at": due_at, "status": status},
            )
