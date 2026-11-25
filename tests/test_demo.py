from io import StringIO
from unittest import skipUnless

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import connection
from django.test import TestCase, override_settings
from django.urls import reverse

from cases.models import Case
from clients.models import Client
from tasks.models import Task


class SeedDemoTests(TestCase):
    @override_settings(DEMO_MODE=False)
    def test_standard_seed_does_not_provision_demo_login(self):
        with self.assertRaises(CommandError):
            call_command("seed_demo", with_demo_user=True, stdout=StringIO())
        self.assertFalse(Client.objects.exists())

        call_command("seed_demo", stdout=StringIO())
        self.assertTrue(Client.objects.exists())
        self.assertFalse(get_user_model().objects.filter(username="demo").exists())

    @skipUnless(getattr(settings, "DEMO_MODE", False) and connection.vendor == "sqlite", "SQLite demo only")
    def test_demo_startup_provisions_login_and_preserves_edits(self):
        stdout = StringIO()
        call_command("seed_demo", with_demo_user=True, stdout=stdout)

        user = get_user_model().objects.get(username="demo")
        self.assertFalse(user.is_staff)
        self.assertIn("Login: demo | Password: legalcrm-demo", stdout.getvalue())
        self.assertTrue(self.client.login(username="demo", password="legalcrm-demo"))
        self.assertEqual(self.client.get(reverse("tasks:dashboard")).status_code, 200)

        seeded_case = Case.objects.get()
        seeded_case.client.full_name = "Учебная карточка после редактирования"
        seeded_case.client.save()
        call_command("seed_demo", with_demo_user=True, stdout=StringIO())

        self.assertEqual(Client.objects.count(), 3)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(Task.objects.count(), 3)
        self.assertEqual(Case.objects.get().client.full_name, "Учебная карточка после редактирования")
