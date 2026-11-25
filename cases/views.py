from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import CaseForm, MaterialFormSet, ParticipantFormSet
from .models import Case


@login_required
def case_list(request):
    query = request.GET.get("q", "").strip()
    stage = request.GET.get("stage", "")
    cases = Case.objects.select_related("client")
    if query:
        cases = cases.filter(
            Q(number__icontains=query)
            | Q(title__icontains=query)
            | Q(client__full_name__icontains=query)
        )
    if stage in Case.Stage.values:
        cases = cases.filter(stage=stage)
    else:
        stage = ""
    return render(
        request,
        "cases/list.html",
        {
            "page_obj": Paginator(cases, 25).get_page(request.GET.get("page")),
            "query": query,
            "stage": stage,
            "stages": Case.Stage.choices,
        },
    )


@login_required
def case_detail(request, pk):
    cases = Case.objects.select_related("client").prefetch_related("participants", "materials", "tasks")
    return render(request, "cases/detail.html", {"case": get_object_or_404(cases, pk=pk)})


@login_required
@require_http_methods(["GET", "POST"])
def case_create(request):
    return case_form_view(request)


@login_required
@require_http_methods(["GET", "POST"])
def case_edit(request, pk):
    return case_form_view(request, pk)


def case_form_view(request, pk=None):
    editing = pk is not None
    if request.method == "POST":
        with transaction.atomic():
            case = get_object_or_404(Case.objects.select_for_update(), pk=pk) if editing else Case()
            form = CaseForm(request.POST, instance=case)
            participants = ParticipantFormSet(request.POST, instance=case)
            materials = MaterialFormSet(request.POST, instance=case)
            validation = (form.is_valid(), participants.is_valid(), materials.is_valid())
            if all(validation):
                form.save()
                participants.save()
                materials.save()
                messages.success(request, "Изменения сохранены." if editing else "Судебное дело создано.")
                return redirect(case)
    else:
        case = get_object_or_404(Case, pk=pk) if editing else Case()
        initial = {} if editing else {"client": request.GET.get("client")}
        form = CaseForm(instance=case, initial=initial)
        participants = ParticipantFormSet(instance=case)
        materials = MaterialFormSet(instance=case)
    return render(
        request,
        "cases/form.html",
        {"case": case, "form": form, "participants": participants, "materials": materials},
    )
