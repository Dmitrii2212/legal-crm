from calendar import Calendar
from collections import defaultdict
from datetime import date, datetime, time, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_safe
from django.views.decorators.vary import vary_on_headers

from cases.models import Case

from .forms import TaskForm
from .models import Task


@login_required
def dashboard(request):
    now = timezone.localtime()
    today = now.date()
    today_start = timezone.make_aware(datetime.combine(today, time.min))
    tomorrow = timezone.make_aware(datetime.combine(today + timedelta(days=1), time.min))
    records = Task.objects.select_related("case")
    active = records.exclude(status=Task.Status.DONE)

    groups = [
        {
            "title": "Сегодня",
            "tasks": records.filter(
                Q(due_at__gte=now) | Q(status=Task.Status.DONE),
                due_at__gte=today_start,
                due_at__lt=tomorrow,
            ),
            "empty": "На сегодня больше ничего не запланировано.",
            "modifier": "today",
        },
        {
            "title": "Просрочено",
            "tasks": active.filter(due_at__lt=now),
            "empty": "Просроченных задач и сроков нет.",
            "modifier": "overdue",
        },
        {
            "title": "Предстоит",
            "tasks": active.filter(due_at__gte=tomorrow),
            "empty": "Предстоящих задач и сроков нет.",
            "modifier": "upcoming",
        },
    ]
    return render(request, "tasks/dashboard.html", {"today": today, "groups": groups})


def first_day_of_month(value, today):
    if value and len(value) == 7:
        try:
            return date.fromisoformat(f"{value}-01")
        except ValueError:
            pass
    return today.replace(day=1)


@vary_on_headers("HX-Request", "HX-History-Restore-Request")
@require_safe
def calendar_view(request):
    hx_navigation = (
        request.headers.get("HX-Request") == "true"
        and request.headers.get("HX-History-Restore-Request") != "true"
    )
    if not request.user.is_authenticated:
        login_redirect = redirect_to_login(request.get_full_path())
        if hx_navigation:
            return HttpResponse(headers={"HX-Redirect": login_redirect.url})
        return login_redirect

    today = timezone.localdate()
    first = first_day_of_month(request.GET.get("month"), today)
    previous = (first - timedelta(days=1)).replace(day=1) if first > date.min else None
    following = None
    if (first.year, first.month) != (date.max.year, date.max.month):
        following = (
            date(first.year + 1, 1, 1)
            if first.month == 12
            else first.replace(month=first.month + 1)
        )

    tasks = Task.objects.select_related("case")
    if first > date.min:
        start_at = timezone.make_aware(datetime.combine(first, time.min))
        tasks = tasks.filter(due_at__gte=start_at)
    if following:
        end_at = timezone.make_aware(datetime.combine(following, time.min))
        tasks = tasks.filter(due_at__lt=end_at)

    tasks_by_day = defaultdict(list)
    for task in tasks:
        tasks_by_day[timezone.localtime(task.due_at).date()].append(task)

    weeks = []
    for week in Calendar().monthdayscalendar(first.year, first.month):
        days = []
        for day in week:
            if day:
                day_date = first.replace(day=day)
                days.append({"date": day_date, "tasks": tasks_by_day.get(day_date, ())})
            else:
                days.append(None)
        weeks.append(days)

    context = {
        "month": first,
        "previous_month": previous.isoformat()[:7] if previous else None,
        "following_month": following.isoformat()[:7] if following else None,
        "today": today,
        "weekdays": ("Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"),
        "weeks": weeks,
        "task_count": len(tasks),
        "has_today": (first.year, first.month) == (today.year, today.month),
    }
    template = "tasks/calendar_panel.html" if hx_navigation else "tasks/calendar.html"
    return render(request, template, context)


@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task.objects.select_related("case"), pk=pk)
    return render(request, "tasks/detail.html", {"task": task})


@login_required
def task_create(request, pk=None):
    case = get_object_or_404(Case, pk=pk) if pk is not None else None
    form = TaskForm(request.POST if request.method == "POST" else None, fixed_case=case)
    if request.method == "POST" and form.is_valid():
        task = form.save()
        messages.success(request, "Запись создана.")
        return redirect(task)
    return render(request, "tasks/form.html", {"form": form, "case": case})


@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task.objects.select_related("case"), pk=pk)
    form = TaskForm(request.POST if request.method == "POST" else None, instance=task)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Изменения сохранены.")
        return redirect(task)
    return render(request, "tasks/form.html", {"form": form, "task": task})
