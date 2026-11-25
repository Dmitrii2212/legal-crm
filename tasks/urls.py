from django.urls import path

from . import views

app_name = "tasks"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("calendar/", views.calendar_view, name="calendar"),
    path("tasks/new/", views.task_create, name="create"),
    path("tasks/<int:pk>/", views.task_detail, name="detail"),
    path("tasks/<int:pk>/edit/", views.task_edit, name="edit"),
    path("cases/<int:pk>/tasks/new/", views.task_create, name="create_for_case"),
]
