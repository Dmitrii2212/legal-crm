from datetime import UTC, datetime, time, timedelta
from zoneinfo import ZoneInfo

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client as BrowserClient
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from cases.models import Case, CaseMaterial, CaseParticipant
from clients.models import Client
from tasks.models import Task


class AuthenticationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="demo-lawyer", password="workflow-test-password"
        )

    def test_protected_pages_and_login_logout(self):
        calendar_url = reverse("tasks:calendar")
        protected_urls = [
            reverse("tasks:dashboard"),
            calendar_url,
            reverse("tasks:create"),
            reverse("clients:list"),
            reverse("clients:create"),
            reverse("cases:list"),
            reverse("cases:create"),
        ]
        login_url = reverse("login")
        for path in protected_urls:
            with self.subTest(path=path):
                self.assertRedirects(self.client.get(path), f"{login_url}?next={path}")

        htmx_response = self.client.get(
            calendar_url, headers={"HX-Request": "true"}
        )
        self.assertEqual(htmx_response.status_code, 200)
        self.assertEqual(
            htmx_response.headers["HX-Redirect"], f"{login_url}?next={calendar_url}"
        )
        self.assertEqual(htmx_response.content, b"")
        self.assertRedirects(
            self.client.post(
                login_url,
                {
                    "username": self.user.username,
                    "password": "workflow-test-password",
                    "next": reverse("cases:create"),
                },
            ),
            reverse("cases:create"),
        )
        self.assertEqual(self.client.get(reverse("tasks:dashboard")).status_code, 200)
        self.assertEqual(self.client.post(reverse("logout")).status_code, 302)
        self.assertRedirects(
            self.client.get(reverse("tasks:dashboard")),
            f"{login_url}?next={reverse('tasks:dashboard')}",
        )

    def test_authenticated_writes_require_csrf(self):
        browser = BrowserClient(enforce_csrf_checks=True)
        browser.force_login(self.user)
        path = reverse("clients:create")
        data = {"client_type": Client.Type.PERSON, "full_name": "Тестов Семён Примерович"}

        self.assertEqual(browser.post(path, data).status_code, 403)
        self.assertFalse(Client.objects.filter(full_name=data["full_name"]).exists())
        self.assertEqual(browser.get(path).status_code, 200)
        data["csrfmiddlewaretoken"] = browser.cookies[settings.CSRF_COOKIE_NAME].value
        self.assertEqual(browser.post(path, data).status_code, 302)
        self.assertTrue(Client.objects.filter(full_name=data["full_name"]).exists())


class LegalWorkflowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username="test-operator")

    def setUp(self):
        self.client.force_login(self.user)

    def assert_form_saved(self, response):
        errors = {}
        if response.context is not None:
            for name in ("form", "participants", "materials"):
                form = response.context.get(name)
                if form is not None:
                    errors[name] = str(form.errors)
        self.assertEqual(response.status_code, 302, str(errors))

    def test_create_all_client_types_and_edit_contact_details(self):
        clients = [
            (Client.Type.PERSON, "Образцова Полина Тестовна"),
            (Client.Type.SOLE_PROPRIETOR, "ИП Примеров Самуил Условный"),
            (Client.Type.COMPANY, 'ООО «Учебный маяк»'),
        ]
        for client_type, full_name in clients:
            with self.subTest(client_type=client_type):
                response = self.client.post(
                    reverse("clients:create"),
                    {"client_type": client_type, "full_name": full_name},
                )
                self.assert_form_saved(response)
                customer = Client.objects.get(full_name=full_name)
                self.assertEqual(customer.client_type, client_type)
                self.assertRedirects(response, reverse("clients:detail", args=[customer.pk]))
                self.assertContains(self.client.get(response.url), "Редактировать")

        customer = Client.objects.get(full_name=clients[-1][1])
        response = self.client.post(
            reverse("clients:edit", args=[customer.pk]),
            {
                "client_type": Client.Type.COMPANY,
                "full_name": customer.full_name,
                "email": "mayak@example.test",
                "contact_name": "Дежурный представитель",
            },
        )
        self.assert_form_saved(response)
        customer.refresh_from_db()
        self.assertEqual(customer.email, "mayak@example.test")
        self.assertEqual(customer.contact_name, "Дежурный представитель")
        listing = self.client.get(reverse("clients:list"))
        for _, full_name in clients:
            self.assertContains(listing, full_name)

    def test_case_and_task_workflow(self):
        response = self.client.post(
            reverse("clients:create"),
            {"client_type": Client.Type.COMPANY, "full_name": "Учебная организация"},
        )
        self.assert_form_saved(response)
        customer = Client.objects.get(full_name="Учебная организация")
        case_form = {
            "number": "А00-12345/2026",
            "title": "Учебный спор о поставке",
            "client": customer.pk,
            "court_name": "Тестовый арбитражный суд",
            "court_details": "Учебный адрес, кабинет 10",
            "judge": "Примерова А. А.",
            "stage": "first_instance",
            "participants-TOTAL_FORMS": "2",
            "participants-INITIAL_FORMS": "0",
            "participants-MIN_NUM_FORMS": "0",
            "participants-MAX_NUM_FORMS": "100",
            "participants-0-name": "Учебная организация",
            "participants-0-role": "claimant",
            "participants-0-client": customer.pk,
            "participants-1-name": "Модельный поставщик",
            "participants-1-role": "respondent",
            "materials-TOTAL_FORMS": "1",
            "materials-INITIAL_FORMS": "0",
            "materials-MIN_NUM_FORMS": "0",
            "materials-MAX_NUM_FORMS": "100",
            "materials-0-title": "Учебная карточка дела",
            "materials-0-url": "https://example.test/cases/1",
        }
        response = self.client.post(reverse("cases:create"), case_form)
        self.assert_form_saved(response)
        case = Case.objects.get(number=case_form["number"])
        self.assertEqual(case.client, customer)
        self.assertEqual(case.court_name, case_form["court_name"])
        self.assertEqual(case.court_details, case_form["court_details"])
        self.assertEqual(case.judge, case_form["judge"])
        self.assertEqual(case.stage, case_form["stage"])
        case_url = reverse("cases:detail", args=[case.pk])
        self.assertRedirects(response, case_url)
        case_page = self.client.get(case_url)
        self.assertContains(case_page, "Модельный поставщик")
        self.assertContains(case_page, "https://example.test/cases/1")
        claimant = CaseParticipant.objects.get(case=case, role="claimant")
        respondent = CaseParticipant.objects.get(case=case, role="respondent")
        material = CaseMaterial.objects.get(case=case)
        self.assertEqual(claimant.client, customer)

        edit_url = reverse("cases:edit", args=[case.pk])
        case_form.update(
            {
                "title": "Учебный спор о поставке в апелляции",
                "stage": "appeal",
                "participants-INITIAL_FORMS": "2",
                "participants-0-id": claimant.pk,
                "participants-1-id": respondent.pk,
                "participants-1-DELETE": "on",
                "materials-INITIAL_FORMS": "1",
                "materials-0-id": material.pk,
                "materials-0-url": "https://example.test/cases/1/appeal",
            }
        )
        invalid_form = {**case_form, "materials-0-url": "неверный адрес"}
        self.assertEqual(self.client.post(edit_url, invalid_form).status_code, 200)
        case.refresh_from_db()
        self.assertEqual(case.stage, "first_instance")
        self.assertTrue(CaseParticipant.objects.filter(pk=respondent.pk).exists())
        material.refresh_from_db()
        self.assertEqual(material.url, "https://example.test/cases/1")

        response = self.client.post(edit_url, case_form)
        self.assert_form_saved(response)
        self.assertRedirects(response, case_url)
        case.refresh_from_db()
        material.refresh_from_db()
        self.assertEqual(case.stage, "appeal")
        self.assertEqual(case.title, case_form["title"])
        self.assertEqual(material.url, case_form["materials-0-url"])
        self.assertFalse(CaseParticipant.objects.filter(pk=respondent.pk).exists())

        today = timezone.localdate()
        due = datetime.combine(today, time(16, 30))
        task_form = {
            "title": "Подготовить учебные пояснения",
            "kind": "task",
            "due_at": due.isoformat(timespec="minutes"),
            "status": "open",
            "description": "Пример задания без реальных данных",
        }
        task_create_url = reverse("tasks:create_for_case", args=[case.pk])
        self.assertContains(self.client.get(case_url), task_create_url)
        response = self.client.post(task_create_url, task_form)
        self.assert_form_saved(response)
        task = Task.objects.get(title=task_form["title"])
        task_url = reverse("tasks:detail", args=[task.pk])
        self.assertRedirects(response, task_url)
        self.assertEqual(task.case, case)
        self.assertEqual(task.due_at, due.replace(tzinfo=ZoneInfo("Europe/Moscow")))

        deadline_title = "Учебный контрольный срок"
        response = self.client.post(
            reverse("tasks:create"),
            {
                **task_form,
                "case": case.pk,
                "title": deadline_title,
                "kind": "deadline",
                "due_at": (due + timedelta(days=1)).isoformat(timespec="minutes"),
            },
        )
        self.assert_form_saved(response)
        deadline = Task.objects.get(title=deadline_title)
        self.assertEqual(deadline.case, case)
        self.assertEqual(deadline.kind, "deadline")

        dashboard = self.client.get(reverse("tasks:dashboard"))
        self.assertContains(dashboard, task.title)
        self.assertContains(dashboard, deadline.title)
        self.assertContains(dashboard, task_url)
        current_month = self.client.get(
            reverse("tasks:calendar"), {"month": today.strftime("%Y-%m")}
        )
        self.assertContains(current_month, task.title)
        self.assertContains(current_month, "16:30")

        new_due = due.replace(hour=18, minute=15)
        task_form.update(
            {
                "case": case.pk,
                "status": "done",
                "title": "Пояснения готовы",
                "due_at": new_due.isoformat(timespec="minutes"),
            }
        )
        response = self.client.post(reverse("tasks:edit", args=[task.pk]), task_form)
        self.assert_form_saved(response)
        self.assertRedirects(response, task_url)
        task.refresh_from_db()
        self.assertEqual(task.status, "done")
        self.assertEqual(task.title, task_form["title"])
        self.assertEqual(task.due_at, new_due.replace(tzinfo=ZoneInfo("Europe/Moscow")))
        self.assertContains(self.client.get(task_url), task.title)

    def test_calendar_uses_moscow_day_for_full_and_htmx_pages(self):
        customer = Client.objects.create(
            client_type=Client.Type.PERSON, full_name="Учебный клиент календаря"
        )
        case = Case.objects.create(
            client=customer,
            number="А00-98765/2026",
            title="Учебное дело для календаря",
            court_name="Тестовый арбитражный суд",
        )
        task = Task.objects.create(
            case=case,
            title="Учебный срок на границе месяца",
            kind="deadline",
            status="open",
            due_at=datetime(2026, 11, 30, 21, 15, tzinfo=UTC),
        )
        calendar_url = reverse("tasks:calendar")

        november = self.client.get(calendar_url, {"month": "2026-11"})
        self.assertNotContains(november, task.title)
        december = self.client.get(calendar_url, {"month": "2026-12"})
        self.assertContains(december, task.title)
        self.assertContains(december, "00:15")
        self.assertTrue(december.content.lstrip().lower().startswith(b"<!doctype html>"))

        partial = self.client.get(
            calendar_url, {"month": "2026-12"}, headers={"HX-Request": "true"}
        )
        self.assertContains(partial, 'id="calendar-panel"')
        self.assertContains(partial, task.title)
        self.assertFalse(partial.content.lstrip().lower().startswith(b"<!doctype html>"))
        self.assertIn("HX-Request", partial.headers["Vary"])

        restored = self.client.get(
            calendar_url,
            {"month": "2026-12"},
            headers={"HX-Request": "true", "HX-History-Restore-Request": "true"},
        )
        self.assertContains(restored, task.title)
        self.assertTrue(restored.content.lstrip().lower().startswith(b"<!doctype html>"))
