from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from config.forms import LoginForm

admin.site.site_header = "Управление Legal CRM"
admin.site.site_title = "Legal CRM"
admin.site.index_title = "Управление рабочим пространством"

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "login/",
        auth_views.LoginView.as_view(authentication_form=LoginForm, redirect_authenticated_user=True),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("clients/", include("clients.urls")),
    path("cases/", include("cases.urls")),
    path("", include("tasks.urls")),
]
