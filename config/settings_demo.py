from .settings_base import *

DEMO_MODE = True
DEBUG = True
SECRET_KEY = "django-insecure-legal-crm-sqlite-demo-only"
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
SESSION_COOKIE_NAME = "legalcrm_demo_sessionid"
CSRF_COOKIE_NAME = "legalcrm_demo_csrftoken"
WHITENOISE_AUTOREFRESH = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "demo.sqlite3",
    },
}
